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

$`E = \frac{1}{2}\ * J * (2 * \pi\ * f)^2`$

$`J`$ = total inertia

$`f`$ = rotation frequency 

## energy stored in DC bus

$`E = \frac{1}{2}\ * C * U^2`$

$`C`$ = total capacitance

$`U`$ = DC bus voltage

## inertia reduced by gear

$`Jred = \frac{J}{(i^2)}\ `$

$`i`$ = gear reduction (>1)

## power

$`P = 2 * \pi\ * f * M`$

$`M`$ = torque

$`f`$ = rotation frequency 

## torque constant of an induction motor

$`kt = \frac{3*lh^2*zp*im}{2*(lm+lr)}\ `$

$`zp`$ = MOTOR_POLEPAIRS

$`lh`$ = MOTOR_MUTUAL_INDUCTANCE

$`lr`$ = MOTOR_ROTOR_INDUCTANCE

$`im`$ = $`\sqrt(2)`$ * MOTOR_MAGNETIZING_CURR

