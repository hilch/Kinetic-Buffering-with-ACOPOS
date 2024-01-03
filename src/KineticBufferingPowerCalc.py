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
                 iGear = 1.0,
                 loadInertia = 0.0, 
                 speedPowerfail = 10.0, 
                 Pfriction = 0, 
                 UDC_NOMINAL = 750,
                 DCbusCapacity = 1650
                   ):
        '''

        Args:
            aptfile : ACOPOS parameter file with motor specification *.apt
            iGear : gear ratio
            loadInertia : load inertia [kgm^2]
            speedPowerfail : gear shaft speed in case of powerfail [1/s]
            Pfriction : fiction power which consumes the kinetic energy, e.g. MOTOR_TERMINAL_POWER  [W]
            UDC_NOMINAL : nominal DC bus voltage before powerfail
            DCbusCapacity : DC bus capacity [µF]
        '''

        self.motorShaftInertia = loadInertia / iGear**2
        self.nPowerFail = speedPowerfail * iGear # motor shaft speed in case of powerfail [1/s]
        self.Pfriction = Pfriction
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

            omega = 2 * np.pi * self.nPowerFail
            self.Erot = 1/2 * (self.MOTOR_INERTIA + self.motorShaftInertia) * omega**2 # [Ws]
            pass

        else:
            raise TypeError(f"{aptfile} does not contain an ACOPOS parameter table !")


    def _plotPregen(self, ax, Pregen, Pregen0, iq, n, n0):
        '''
        plot regenerative power as function of current
        '''
        for i in range( len(n)):
            ax.plot( iq, Pregen[i], '--')
        ax.plot(iq, Pregen0, 'r', linewidth=2)
        ax.set_xlabel('quadrature current [A]')
        ax.set_ylabel('regenerative power [W]')
        ax.legend(['n = ' + str(round(n, 2)) for n in n] + ['n0 = ' + str(round(n0, 2))])
        ax.grid(True)


    def _plotPshaft(self, ax, Pshaft, iq, n, n0):
        '''
        plot motor shaft power as function of current
        '''
        for i in range(len(n)):
            ax.plot(iq, Pshaft[i], '--')
        ax.set_xlabel('quadrature current [A]')
        ax.set_ylabel('shaft power [W]')
        ax.legend(['n = ' + str(round(n, 2)) for n in n] + ['n0 = ' + str(round(n0, 2))])
        ax.grid(True)


    def _plotPloss(self, ax, Ploss, iq ):
        '''
        plot power loss as function of current
        '''
        pf = np.ones(101)*self.Pfriction
        ax.plot(iq, Ploss, 'r')
        ax.plot(iq, pf, 'b') 
        ax.axvline(x=self.iqBuffer, color='r', linestyle='--') # mark buffer current               
        ax.set_xlabel('quadrature current [A]')
        ax.set_ylabel('loss power [W]')
        ax.legend(['Ploss Cu', 'Ploss friction'])
        ax.grid(True)        


    def _plotBufferDuration(self, ax, Ploss, iq ):
        '''
        buffer duration as function of (normalized) current
        '''
        #iqNormalized = np.divide( iq, iqmax)
        PlossTotal = Ploss + self.Pfriction # total power loss
        t = np.divide(self.Erot + self.Ecap, PlossTotal, where=PlossTotal!=0) # buffering time
        tBuffer = np.where(t <= 60, t, 60) # Replace values above the maximum

        ax.plot(iq, tBuffer, 'g')
        ax.axvline(x=self.iqBuffer, color='r', linestyle='--') # mark buffer current
        ax.set_xlabel('quadrature current [A]')
        ax.set_ylabel('time [s]')
        ax.grid(True)      


    def _plotPowerSynchronous(self, axs):
        '''
        synchronous motor
        '''
        Kt = self.MOTOR_TORQ_CONST
        Rspp = self.MOTOR_STATOR_RESISTANCE
        nN = 100/60
        n0 = self.nPowerFail
        iqmax = self.MOTOR_CURR_MAX * np.sqrt(2)
        n = np.linspace(0, nN, 11)
        iq = np.linspace(0, iqmax, 101)

        self.iqBuffer = self.Pfriction/(2*np.pi*self.nPowerFail*Kt)*np.sqrt(2)

        Ploss = 3/2* iq**2 * Rspp/2 # loss due to stator resistance
        Pshaft = Kt / np.sqrt(2) * 2 * np.pi * np.outer( n, iq)
        Pregen = Pshaft - Ploss
        Pregen0 = Kt / np.sqrt(2) * 2 * np.pi * n0 * iq - Ploss

        self._plotPregen( axs[0,0], Pregen, Pregen0, iq, n, n0 )
        self._plotPshaft( axs[0,1], Pshaft, iq, n, n0 )
        self._plotPloss( axs[0,2], Ploss, iq )
        self._plotBufferDuration( axs[1,0], Ploss, iq )



    def _plotPowerInduction(self, axs):
        '''
        induction motor
        '''        
        fpolepairs = self.MOTOR_POLEPAIRS
        i0 = np.sqrt(2) * self.MOTOR_MAGNETIZING_CURR
        lh = self.MOTOR_MUTUAL_INDUCTANCE
        lr = self.MOTOR_MUTUAL_INDUCTANCE + self.MOTOR_ROTOR_INDUCTANCE
        rs = self.MOTOR_STATOR_RESISTANCE

        lr_inv = 1 / lr
        kt_nom = 1.5 * np.sqrt(2) * fpolepairs * lh**2 * lr_inv * i0
        kt = np.sqrt(2) * kt_nom

        n = np.linspace(0, self.MOTOR_SPEED_RATED/60, 11)
        n0 = self.nPowerFail
        iqmax = self.MOTOR_CURR_MAX * np.sqrt(2)        
        iq = np.linspace(0, iqmax, 101)

        self.iqBuffer = self.Pfriction/(2*np.pi*self.nPowerFail*kt)*np.sqrt(2)

        Ploss = 3/2 * iq**2 * rs + 3/2 * i0**2 * rs # power loss due to stator resistance
        Pshaft = kt / np.sqrt(2) * 2 * np.pi * np.outer(n, iq)
        Pregen0 = kt / np.sqrt(2) * 2 * np.pi * n0 * iq - Ploss
        Pregen = Pshaft - Ploss

        self._plotPregen( axs[0,0], Pregen, Pregen0, iq, n, n0 )
        self._plotPshaft( axs[0,1], Pshaft, iq, n, n0 )
        self._plotPloss( axs[0,2], Ploss, iq )
        self._plotBufferDuration( axs[1,0], Ploss, iq)

    def plotPower(self):
        fig, axs = plt.subplots(2, 3)

        fig.suptitle(f'KIB: {self.motorName} ({self.motorType})' , fontsize=16)        
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
            f'n0 (motor shaft speed @ powerfail) = { round(self.nPowerFail,2)} 1/s',
            f'P Friction = { round(self.Pfriction)} W',
            f'E rotation = { round(self.Erot/1000)} kJ',
            f'E DC bus capacity = { round(self.Ecap/1000)} kJ',
            f'iq KIB = { round(self.iqBuffer,1)} A'                                        
        )
        for n,text in enumerate(preconditions):
          axs[1,2].text( 0, 1-n*0.05, text, fontsize=12 )      


        # save plot
        s = 'KIB-' + self.motorName
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
        plt.savefig( fname = self.motorName + '.pdf' )
        #plt.show()                    
        

if __name__ == '__main__':
    # example torque motor
    motor = Axis("530d12f.apt", iGear=1, loadInertia= 4270, speedPowerfail=1.5, 
                                Pfriction=7000, UDC_NOMINAL= 620, 
                                DCbusCapacity= 1650 + 0.22 + 990 + 8 * 990 # 8BVP0880 + 8B0C0320 + 8BVI0440 + 8*8BVI0330
                                )
    motor.plotPower() 
 
    # example induction motor with gear
    motor = Axis("2kj3507p.apt", iGear = 25, loadInertia=4270, speedPowerfail=1.5, 
                                Pfriction=7000, UDC_NOMINAL= 620, 
                                DCbusCapacity= 1650 + 0.22 + 990 + 8 * 990 # 8BVP0880 + 8B0C0320 + 8BVI0440 + 8*8BVI0330
                                )
    motor.plotPower()



