# KineticBufferingPowerCalc.py
# https://github.com/hilch/Kinetic-Buffering-with-ACOPOS

import matplotlib.pyplot as plt
import numpy as np
import xml.etree.ElementTree as ET
from math import sqrt

class Axis:
    '''
    ACOPOS driven master axis used for kinetic buffering
    '''
    def __init__(self, aptfile, 
                 description = "",
                 iGear = 1.0,
                 loadInertia = 0.0, 
                 speedPowerfail = 10.0, 
                 frictionTorque = 0, 
                 UDC_NOMINAL = 750,
                 DCbusCapacity = 1650,
                 lineResistance = 0.0
                   ):
        '''

        Args:
            aptfile : ACOPOS parameter file with motor specification *.apt
            description : description printed on top of sheet
            iGear : gear ratio
            loadInertia : load inertia [kgm^2]
            speedPowerfail : gear shaft speed in case of powerfail [1/s]
            frictionTorque : fiction torque which consumes the kinetic energy
            UDC_NOMINAL : nominal DC bus voltage before powerfail
            DCbusCapacity : DC bus capacity [µF]
            lineResistance: Resistance of one line beetween ACOPOS-connector and motor-connector
        '''

        self.description = description
        self.motorShaftInertia = loadInertia / iGear**2
        self.speedPowerfail = speedPowerfail
        self.n0 = speedPowerfail * iGear # motor shaft speed in case of powerfail [1/s]
        self.frictionTorque = frictionTorque
        self.frictionTorqueShaft = frictionTorque / iGear
        self.lineResistance = lineResistance
        self.Ecap = 1/2 * (DCbusCapacity/1.0e6) * UDC_NOMINAL**2  # electrical energy before powerfail

        # read ACOPOS parameter table with motor specification
        tree = ET.parse(aptfile)
        root = tree.getroot()
        if root.tag == 'AcoposParameterTable':
            parameters = root[0]
            if( parameters.tag == 'Root' and parameters.attrib == {'Name':'Parameters'}):
                motor = parameters[0]
                self.motorName = motor.attrib.get('Name')
                for g in motor:
                    if g.tag == 'Group':
                        for p in g:
                            value = p.attrib.get("Value")
                            if value.startswith('0x'):
                                value = int(value,16)
                            else:
                                value = value.replace(',','.')
                                value = float(value)

                            match p.attrib.get("Name"):
                                case 'MOTOR_TYPE':
                                    self.MOTOR_TYPE = value
                                    match self.MOTOR_TYPE:
                                        case 1 |3:
                                            self.motorType = 'ASM' # induction
                                        case 2 | 4:
                                            self.motorType = 'SM' # synchronous
                                case 'MOTOR_TORQ_CONST':
                                    self.MOTOR_TORQ_CONST = value
                                case 'MOTOR_CURR_MAX':
                                    self.MOTOR_CURR_MAX = value
                                case 'MOTOR_POLEPAIRS':
                                    self.MOTOR_POLEPAIRS = int(value)
                                case 'MOTOR_STATOR_RESISTANCE':
                                    self.MOTOR_STATOR_RESISTANCE = value
                                case 'MOTOR_MAGNETIZING_CURR':
                                    self.MOTOR_MAGNETIZING_CURR = value
                                case 'MOTOR_MUTUAL_INDUCTANCE':
                                    self.MOTOR_MUTUAL_INDUCTANCE = value
                                case 'MOTOR_ROTOR_INDUCTANCE':
                                    self.MOTOR_ROTOR_INDUCTANCE = value
                                case 'MOTOR_SPEED_RATED':
                                    self.MOTOR_SPEED_RATED = value
                                case 'MOTOR_INERTIA':
                                    self.MOTOR_INERTIA = value

            omega0 = 2 * np.pi * self.n0
            self.Erot = 1/2 * (self.MOTOR_INERTIA + self.motorShaftInertia) * omega0**2 # [Ws]
            pass

        else:
            raise TypeError(f"{aptfile} does not contain an ACOPOS parameter table !")


    def _plotPregen(self, ax, Pregen, Pregen0, iq, n):
        '''
        plot regenerative power as function of current
        '''
        for i in range( len(n)):
            ax.plot( iq, Pregen[i], '--')
        ax.plot(iq, Pregen0, 'r', linewidth=2)
        ax.set_xlabel('quadrature current [A]')
        ax.set_ylabel('regenerative power [W]')
        ax.legend(['n = ' + str(round(n, 2)) for n in n] + ['n0 = ' + str(round(self.n0, 2))])
        ax.grid(True)


    def _plotPshaft(self, ax, Pshaft, Pshaft0, iq, n):
        '''
        plot motor shaft power as function of current
        '''
        for i in range(len(n)):
            ax.plot(iq, Pshaft[i], '--')
        ax.plot(iq, Pshaft0, 'r', linewidth=2)            
        ax.set_xlabel('quadrature current [A]')
        ax.set_ylabel('shaft power [W]')
        ax.legend(['n = ' + str(round(n, 2)) for n in n] + ['n0 = ' + str(round(self.n0, 2))])
        ax.grid(True)


    def _plotPloss(self, ax, Ploss, iq ):
        '''
        plot power loss as function of current
        '''
        pf = np.ones(101)* (2 * np.pi * self.n0 * self.frictionTorqueShaft)
        ax.plot(iq, Ploss, 'r')
        ax.plot(iq, pf, 'b') 
        ax.axvline(x=self.iqBuffer, color='r', linestyle='--') # mark buffer current               
        ax.set_xlabel('quadrature current [A]')
        ax.set_ylabel('loss power [W]')
        ax.legend(['Ploss Cu', 'Ploss friction'])
        ax.grid(True)        


    def _plotEnergyConsumption(self, ax ):
        '''
        buffer duration as function of (normalized) current
        '''
        t = np.linspace(0.001,self.tBuffer,100)
        E = np.linspace( (self.Erot+self.Ecap)/1000, 0.001,100)

        ax.plot(t, E, 'g')
        ax.set_xlabel('time [s]')
        ax.set_ylabel('Energy [kJ]')
        ax.grid(True)      



    def _plotPowerSynchronous(self, axs):
        '''
        synchronous motor
        '''
        Kt = self.MOTOR_TORQ_CONST
        Rspp = self.MOTOR_STATOR_RESISTANCE
        nN = 100/60
        iqmax = self.MOTOR_CURR_MAX * np.sqrt(2)
        n = np.linspace(0, nN, 11)
        iq = np.linspace(0, iqmax, 101)

        self.iqBuffer = self.frictionTorqueShaft/Kt*np.sqrt(2) # iq at the time of buffering

        Ploss = 3/2* iq**2 * (Rspp/2 + self.lineResistance) # loss due to copper resistance
        Ploss0 = 3/2* self.iqBuffer**2 * (Rspp/2 + self.lineResistance) 

        Pshaft = Kt / np.sqrt(2) * 2 * np.pi * np.outer( n, iq)
        Pregen = Pshaft - Ploss
        Pshaft0 = Kt / np.sqrt(2) * 2 * np.pi * self.n0 * iq
        Pregen0 = Pshaft0 - Ploss

        self.tBuffer = (self.Erot+self.Ecap)/(Ploss0 + 2 * np.pi * self.n0 * self.frictionTorqueShaft) # max. buffer duration

        self._plotPregen( axs[0,0], Pregen, Pregen0, iq, n )
        self._plotPshaft( axs[0,1], Pshaft, Pshaft0, iq, n )
        self._plotPloss( axs[0,2], Ploss, iq )
        self._plotEnergyConsumption( axs[1,0] )



    def _plotPowerInduction(self, axs):
        '''
        induction motor
        '''        
        zp = self.MOTOR_POLEPAIRS
        im = np.sqrt(2) * self.MOTOR_MAGNETIZING_CURR
        lh = self.MOTOR_MUTUAL_INDUCTANCE
        lr = self.MOTOR_MUTUAL_INDUCTANCE + self.MOTOR_ROTOR_INDUCTANCE
        rs = self.MOTOR_STATOR_RESISTANCE

        lr_inv = 1 / lr
        kt = 1.5 * np.sqrt(2) * zp * lh**2 * lr_inv * im

        n = np.linspace(0, self.MOTOR_SPEED_RATED/60, 11)
        iqmax = self.MOTOR_CURR_MAX * np.sqrt(2)        
        iq = np.linspace(0, iqmax, 101)

        self.iqBuffer = self.frictionTorqueShaft/kt*np.sqrt(2) # iq at the time of buffering

        Ploss = 3/2 * iq**2 * (rs+self.lineResistance) + 3/2 * im**2 * (rs+self.lineResistance) # power loss due to copper resistance
        Ploss0 = 3/2 * self.iqBuffer**2 * (rs+self.lineResistance) + 3/2 * im**2 * (rs+self.lineResistance) # power loss due to copper resistance        
        Pshaft = kt / np.sqrt(2) * 2 * np.pi * np.outer(n, iq)
        Pshaft0 = kt / np.sqrt(2) * 2 * np.pi * self.n0 * iq
        Pregen0 = Pshaft0 - Ploss
        Pregen = Pshaft - Ploss

        self.tBuffer = (self.Erot+self.Ecap)/(Ploss0 + 2 * np.pi * self.n0 * self.frictionTorqueShaft) # max. buffer duration

        self._plotPregen( axs[0,0], Pregen, Pregen0, iq, n )
        self._plotPshaft( axs[0,1], Pshaft, Pshaft0, iq, n )
        self._plotPloss( axs[0,2], Ploss, iq )
        self._plotEnergyConsumption( axs[1,0])


    def plotPower(self):
        fig, axs = plt.subplots(2, 3)
        suptitle = f'KIB: {self.motorName} ({self.motorType})'
        if self.description != "":
            suptitle = suptitle + ' - ' + self.description
        fig.suptitle(suptitle , fontsize=16)        
        # Create a new figure with A3 landscape size (width=16.5, heigth=11.7, )        
        fig.set_size_inches((16.5, 11.7)) 
        fig.set_dpi(200)    
        #fig.text(0.1, 0.1, 'Hello, World!', ha='left')        

        if self.motorType == 'ASM':
            self._plotPowerInduction(axs)
        elif self.motorType == 'SM':
            self._plotPowerSynchronous(axs)

        # print some values 
        axs[1,2].axis('off')
        preconditions = (
            f'speed0 (load speed @ powerfail) = { round(self.speedPowerfail,2)} s^-1',            
            f'n0 (motor shaft speed @ powerfail) = { round(self.n0,2)} s^-1',
            f'M Friction = { round(self.frictionTorque,2)} N',
            f'E rotation = { round(self.Erot/1000)} kJ',
            f'E DC bus capacity = { round(self.Ecap/1000)} kJ',
            f'iq KIB = { round(self.iqBuffer,1)} A',
            f'max. buffer duration = { round(self.tBuffer)} s'                                        
        )
        for n,text in enumerate(preconditions):
          axs[1,2].text( 0, 1-n*0.05, text, fontsize=12 )      


        # save plot
        s = 'KIB-' + self.motorName
        if self.description != '':
            s = s + ' - ' + self.description
        s = s.replace("\\", "_")
        s = s.replace("/", "_")
        s = s.replace(":", "_")
        s = s.replace("*", "_")
        s = s.replace("?", "_")
        s = s.replace("\"", "_")
        s = s.replace("<", "_")
        s = s.replace(">", "_")
        s = s.replace("|", "_")    
        plt.tight_layout()

        plt.savefig( fname = s + '.pdf' )
        #plt.show()                    
        

if __name__ == '__main__':
    lineResistance = 0.0175 * 20 / 16
    MOTOR_TERMINAL_POWER = 7000 # motor regenerative power at time of powerfail
    speedPowerfail = 1.5 # load speed at time of powerfail
    frictionTorque = MOTOR_TERMINAL_POWER/(2*np.pi*speedPowerfail) 
    description = 'idle run'

    # example torque motor
    motor = Axis("530d12f.apt", description=description,
                                iGear=1, loadInertia= 4270, speedPowerfail=speedPowerfail, 
                                frictionTorque=frictionTorque, UDC_NOMINAL= 620, 
                                DCbusCapacity= 1650 + 0.22 + 990 + 8 * 990, # 8BVP0880 + 8B0C0320 + 8BVI0440 + 8*8BVI0330
                                lineResistance= lineResistance
                                )
    motor.plotPower() 
 
    # example induction motor with gear
    motor = Axis("2kj3507p.apt", description=description,
                                iGear = 25, loadInertia=4270, speedPowerfail=speedPowerfail, 
                                frictionTorque=frictionTorque, UDC_NOMINAL= 620, 
                                DCbusCapacity= 1650 + 0.22 + 990 + 8 * 990, # 8BVP0880 + 8B0C0320 + 8BVI0440 + 8*8BVI0330
                                lineResistance= lineResistance
                                )
    motor.plotPower()



