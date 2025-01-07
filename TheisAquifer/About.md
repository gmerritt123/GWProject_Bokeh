# Theis Aquifer Drawdown Application

![TheisGif](https://github.com/user-attachments/assets/5d6830de-ede5-48ba-8dc5-9097d24310c3)

This application illustrates the Theis drawdown solution for a perfectly confined, homogenous and isotropic aquifer of uniform thickness and infinite extent being pumped at a constant rate by a fully penetrating well.

4 Sliders control the key controlling parameters: pumping rate, aquifer transmissivity, aquifer storativity, and time.

Three views illustrate drawdown over time and space as per the Theis Solution:

## Plan View
- Shows radial drawdown contours at the currently selected time under the currently selected slider values (i.e. pumping, T and S)
- Shows the pumping well at 0,0
- Ability to place an observation point anywhere (click anywhere in the plot area) to see associated drawdown over time (bottom right plot)

## Drawdown VS. Distance
- Shows drawdown vs distance at the currently selected time under the currently selected slider values (i.e. pumping, T and S)
- Effectively a cross section "slice" through the well
- Observation point location (as placed in plan view plot) is shown here with the *

## Drawdown VS. Time @Observation Point
- Shows drawdown over time (from time = 0 to time = time slider value) at the currently placed observation point location
