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
    def __init__(self, aptfile, loadInertia, nPowerFail, Pfriction, C ):
        '''

        Args:
            aptfile : ACOPOS parameter file with motor data *.apt
            shaftInertia : additional shaft inertia reduced by gear [kgm^2]
            nPowerFail : shaft speed in case of power failure [1/s]
            Pfriction : fiction power which consumes the kinetic energy, e.g. UDC_ACT * ICTRL_ISQ_ACT [W]
            C : DC bus capacity [F]
        '''
        tree = ET.parse(aptfile)
        root = tree.getroot()
        self.loadInertia = loadInertia
        self.nPowerFail = nPowerFail
        self.Pfriction = Pfriction

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
            self.Erot = 1/2 * (self.MOTOR_INERTIA + self.loadInertia) * omega**2 # [Ws]
            self.Ecap = 1/2 * C * 620**2
            pass

        else:
            raise TypeError(f"{aptfile} does not contain an ACOPOS parameter table !")


    def _plotPregen(self, axs, Pregen, Pregen0, iq, n, n0):
        '''
        plot regenerative power as function of current
        '''
        for i in range( len(n)):
            axs[0, 0].plot( iq, Pregen[i], '--')
        axs[0, 0].plot(iq, Pregen0, 'r', linewidth=2)
        axs[0, 0].set_xlabel('quadrature current [A]')
        axs[0, 0].set_ylabel('regenerative power [W]')
        axs[0, 0].legend(['n = ' + str(round(n, 2)) for n in n] + ['n0 = ' + str(round(n0, 2))])
        axs[0, 0].grid(True)


    def _plotPshaft(self, axs, Pshaft, iq, n, n0):
        '''
        plot motor shaft power as function of current
        '''
        for i in range(len(n)):
            axs[0, 1].plot(iq, Pshaft[i], '--')
        axs[0, 1].set_xlabel('quadrature current [A]')
        axs[0, 1].set_ylabel('shaft power [W]')
        axs[0, 1].legend(['n = ' + str(round(n, 2)) for n in n] + ['n0 = ' + str(round(n0, 2))])
        axs[0, 1].grid(True)


    def _plotPloss(self, axs, Ploss, iq):
        '''
        plot power loss as function of current
        '''
        axs[0, 2].plot(iq, Ploss, 'r')
        axs[0, 2].set_xlabel('quadrature current [A]')
        axs[0, 2].set_ylabel('loss power [W]')
        axs[0, 2].grid(True)        


    def _plotBufferDuration(self, axs, Ploss, Pfriction, iq, iqmax ):
        '''
        buffer duration as function of (normalized) current
        '''
        iqNormalized = np.divide( iq, iqmax)
        PlossTotal = Ploss + self.Pfriction # total power loss
        t = np.divide(self.Erot + self.Ecap, PlossTotal, where=PlossTotal!=0) # buffering time
        tBuffer = np.where(t <= 60, t, 60) # Replace values above the maximum

        axs[1, 0].plot(iqNormalized, tBuffer, 'g')
        axs[1, 0].set_xlabel('quadrature current (norm.)')
        axs[1, 0].set_ylabel('time [s]')
        axs[1, 0].grid(True)      


    def _plotPowerSynchronous(self, axs):
        '''
        synchronous motor
        '''
        Kt = self.MOTOR_TORQ_CONST
        Rspp = self.MOTOR_STATOR_RESISTANCE
        nN = 100/60
        n0 = 0.52
        iqmax = self.MOTOR_CURR_MAX * np.sqrt(2)
        n = np.linspace(0, nN, 11)
        iq = np.linspace(0, iqmax, 101)

        Ploss = 3/2* iq**2 * Rspp/2 # loss due to stator resistance
        Pshaft = Kt / np.sqrt(2) * 2 * np.pi * np.outer( n, iq)
        Pregen = Pshaft - Ploss
        Pregen0 = Kt / np.sqrt(2) * 2 * np.pi * n0 * iq - Ploss

        self._plotPregen( axs, Pregen, Pregen0, iq, n, n0 )
        self._plotPshaft( axs, Pshaft, iq, n, n0 )
        self._plotPloss( axs, Ploss, iq)
        self._plotBufferDuration( axs, Ploss, self.Pfriction, iq, iqmax)



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
        n0 = 0.52
        iqmax = self.MOTOR_CURR_MAX * np.sqrt(2)        
        iq = np.linspace(0, iqmax, 101)

        Ploss = 3/2 * iq**2 * rs + 3/2 * i0**2 * rs # power loss due to stator resistance
        Pshaft = kt / np.sqrt(2) * 2 * np.pi * np.outer(n, iq)
        Pregen0 = kt / np.sqrt(2) * 2 * np.pi * n0 - Ploss
        Pregen = Pshaft - Ploss

        self._plotPregen( axs, Pregen, Pregen0, iq, n, n0 )
        self._plotPshaft( axs, Pshaft, iq, n, n0 )
        self._plotPloss( axs, Ploss, iq)
        self._plotBufferDuration( axs, Ploss, self.Pfriction, iq, iqmax)       


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

        # add preconditions
        axs[1,2].axis('off')
        preconditions = (
            f'n Fail = { round(self.nPowerFail,2)} 1/s',
            f'P Friction = { round(self.Pfriction)} W',
            f'E rotation = { round(self.Erot/1000)} kJ',
            f'E electr. = { round(self.Ecap/1000)} kJ'                        
        )
        for n,text in enumerate(preconditions):
          axs[1,2].text( 0, 1-n*0.05, text, fontsize=12 )      
        # axs[1,2].text( 0.1, 0., f'n Fail = { round(self.nPowerFail,2)} 1/s', fontsize=12 )    
        # axs[1,2].text( 0.1, 0.2, f'P Friction = { round(self.Pfriction)} W', fontsize=12 )          
        # axs[1,2].text( 0.1, 0.3, f'E rotation = { round(self.Erot/1000)} kJ', fontsize=12 )          
        # axs[1,2].text( 0.1, 0.4, f'E electr. = { round(self.Ecap/1000)} kJ', fontsize=12 )          

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
    # example data
    motor = Axis("530d12f.apt", loadInertia= 4270, nPowerFail=1.5, Pfriction=22400, C= 2.64)
    motor.plotPower() 
    i=36   
    motor = Axis("2kj3507p.apt", loadInertia=4270/i**2, nPowerFail=1.5072*i, Pfriction=22400, C= 2.64)
    motor.plotPower()



