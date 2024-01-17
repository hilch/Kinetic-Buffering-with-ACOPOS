# ACOPOS Parameters
## Motor Parameters

The motor parameters must be provided as [*.apt file](https://help.br-automation.com/#/en/4/motion%2Fengineering%2Fmotion_control%2Fcfg_modules%2Fapt%2Fapt.html)

[Synchronous motor](https://help.br-automation.com/#/en/4/ncsoftware%2Facp10_drivefunctions%2Fmotor%2Fsynchronmotor%2Fsynchronmotor_.html) (SM)

[Induction motor](https://help.br-automation.com/#/en/4/ncsoftware%2Facp10_drivefunctions%2Fmotor%2Fasynchronmotor%2Fasynchronmotor_.html) (IM)

## Parameters to be traced on buffering axis
- [STAT_UDC_POWERFAIL](https://help.br-automation.com/#/en/4/ncsoftware%2Facp10_parameter%2Fhtml%2Fstat_udc_powerfail.htm) (367), Power mains status (0 = Ok, 2 = failure)
- [MOTOR_TERMINAL_POWER](https://help.br-automation.com/#/en/4/ncsoftware/acp10_parameter/html/motor_terminal_power.htm) (844), elctrical Power at the motor terminals
- [ICTRL_ISQ_ACT](https://help.br-automation.com/#/en/4/ncsoftware/acp10_parameter/html/ictrl_isq_act.htm) (214), isq, Actual stator current quadrature component
- [ICTRL_ISD_ACT](https://help.br-automation.com/#/en/4/ncsoftware/acp10_parameter/html/ictrl_isd_act.htm) (219), isd, Actual stator current direct component
- [UDC_ACT](https://help.br-automation.com/#/en/4/ncsoftware/acp10_parameter/html/udc_act.htm) (298), udc, Measured DC bus voltage
- [SCTRL_SPEED_ACT](https://help.br-automation.com/#/en/4/ncsoftware/acp10_parameter/html/sctrl_speed_act.htm) (251), CTRL Speed controller: Actual speed
- [MOTOR_TORQUE](https://help.br-automation.com/#/en/4/ncsoftware/acp10_parameter/html/torque_act.htm) (277), Torque

## Parameters to be traced on consuming axes

- [MOTOR_TERMINAL_POWER](https://help.br-automation.com/#/en/4/ncsoftware/acp10_parameter/html/motor_terminal_power.htm) (844), elctrical Power at the motor terminals
- [SCTRL_SPEED_ACT](https://help.br-automation.com/#/en/4/ncsoftware/acp10_parameter/html/sctrl_speed_act.htm) (251), CTRL Speed controller: Actual speed
- [MOTOR_TORQUE](https://help.br-automation.com/#/en/4/ncsoftware/acp10_parameter/html/torque_act.htm) (277), Torque


# Formulas

## kinetic energy of a rotating axis

$`E_{rot} = \frac{1}{2}\ * J * (2 * \pi\ * n)^2`$

$`J`$ = total inertia

$`n`$ = SCTRL_SPEED_ACT

## energy stored in DC bus

$`E_{cap} = \frac{1}{2}\ * C * udc^2`$

$`C`$ = total capacitance

$`udc`$ = UDC_ACT

## inertia reduced by gear

$`Jred = \frac{J}{(r^2)}\ `$

$`r`$ = gear ratio (>1)


## torque factor of an induction motor (IM)

$`kt_{IM} = \frac{\sqrt{2}*3*lh^2*zp*im}{2*(lm+lr)}\ `$

$`zp`$ = MOTOR_POLEPAIRS

$`lh`$ = MOTOR_MUTUAL_INDUCTANCE

$`lr`$ = MOTOR_ROTOR_INDUCTANCE

$`im`$ = $`\sqrt{2}`$ * MOTOR_MAGNETIZING_CURR

## shaft power and torque

$`P_{shaft} = 2 * \pi * n * M`$

$`M = \frac{Kt}{\sqrt{2}}*iq `$

$`n`$ = SCTRL_SPEED_ACT

$`Kt`$ = MOTOR_TORQ_CONST (SM) or $`kt_{IM}`$ (IM)

$`iq`$ = ICTRL_ISQ_ACT


