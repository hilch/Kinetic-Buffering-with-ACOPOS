# ACOPOS Parameters

- motor parameter for synchronous or induction motor (*.apt file)
- MOTOR_TERMINAL_POWER (844), elctrical Power at the motor terminals
- ICTRL_ISQ_ACT (214), isq, Actual stator current quadrature component
- ICTRL_ISD_ACT (219), isd, Actual stator current direct component
- STAT_UDC_POWERFAIL, Power mains status (0 = Ok, 2 = failure)
- UDC_ACT (298), udc, Measured DC bus voltage
- SCTRL_SPEED_ACT (251), CTRL Speed controller: Actual speed


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

$`kt_{ASM} = \frac{\sqrt{2}*3*lh^2*zp*im}{2*(lm+lr)}\ `$

$`zp`$ = MOTOR_POLEPAIRS

$`lh`$ = MOTOR_MUTUAL_INDUCTANCE

$`lr`$ = MOTOR_ROTOR_INDUCTANCE

$`im`$ = $`\sqrt{2}`$ * MOTOR_MAGNETIZING_CURR

## shaft power and torque

$`P_{shaft} = 2 * \pi * n * M`$

$`M = \frac{Kt}{\sqrt{2}}*iq `$

$`n`$ = SCTRL_SPEED_ACT

$`Kt`$ = MOTOR_TORQ_CONST (SM) or $`kt_{ASM}`$ (IM)

$`iq`$ = ICTRL_ISQ_ACT
