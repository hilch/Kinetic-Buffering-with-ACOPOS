[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Made For B&R](https://github.com/hilch/BandR-badges/blob/main/Made-For-BrAutomation.svg)](https://www.br-automation.com)
# Kinetic-Buffering-with-ACOPOS

A moving servo axis can store a considerable amount of kinetic energy. In the event of a power failure, this energy can be used to keep a machine running for a short period of time.

Each B&R ACOPOS servo drive contains all necessary firmware function to do this: see ['Kinetic Buffering'](https://help.br-automation.com/#/en/4/ncsoftware%2Facp10_drivefunctions%2Fleistungseinheit%2Fwechselrichter%2Fkinetische_pufferung%2Fkinetische_pufferung_.html)

the energy available when the mains is switched off is consumed by various practical effects:

- external load (axes) connected to DC bus
- friction
- loss in motor resistances
- loss in motor cable
- loss in power stage

This script tries to estimate the maximum buffering time depending on certain system parameters.

[some technical information](documentation.md)




