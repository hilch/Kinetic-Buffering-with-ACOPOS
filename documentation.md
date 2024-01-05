# ACOPOS Parameters

- motor parameter for synchronous or induction motor (*.apt file)
- MOTOR_TERMINAL_POWER (844), elctrical Power at the motor terminals
- ICTRL_ISQ_ACT (214), isq, Actual stator current quadrature component
- ICTRL_ISD_ACT (219), isd, Actual stator current direct component
- UDC_ACT (298), udc, Measured DC bus voltage
- SCTRL_SPEED_ACT (251), CTRL Speed controller: Actual speed

# Formulas

## kinetic energy of a rotating axis

$`E = \frac{1}{2}\ * J * (2 * \pi\ * f)^2`$

$`J`$ = total inertia

$`f`$ = rotation frequency 

### energy stored in DC bus

$`E = \frac{1}{2}\ * C * U^2`$

$`C`$ = total capacitance

$`U`$ = DC bus voltage

### power
