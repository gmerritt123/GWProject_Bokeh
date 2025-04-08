# Reservoir Water Balance

This application visualizes and tests the feasibility of a conceptual water balance on a hypothetical reservoir from 2019 to 2023. It combines observational data, hydrologic model outputs from [Raven](https://raven.uwaterloo.ca/), and allows for real-time adjustment of two key parameters.  
  ![WB](https://github.com/user-attachments/assets/d410e089-f861-4dc2-9e83-8900b7abb36a)

**Observed components of the water balance consist of:**

*   Precipitation over the reservoir (via climate data)
*   Creek inflows (via flow monitoring)
*   Dam outflows (via flow monitoring)
*   Reservoir depth over time (via pressure transducers)

**Simulated components of the water balance consist of:**

*   Groundwater inflow: A fraction of the recharge signal (simulated by Raven) within the reservoir's catchment discharges to the reservoir. This is often referred to as "baseflow" or "interflow". This fraction is adjustable with a slider.
*   Runoff: the amount of precipitation thats runs off the catchment directly to the reservoir, as simulated by Raven
*   Actual evapotranspiration (AET) - Based on reservoir surface area and potential evapotranspiration (estimated from climate data)
*   Groundwater outflow: Water seeping out of the reservoir (usually near the dam). The rate depends on reservoir depth and material permeability, which (for this application) is highly simplified into a single adjustable coefficient.

**How it works:**  
  
A predefined reservoir depth-volume-surface area relationship is used to calculate a transient water balance. At each time step, inflows are summed, reservoir depth/surface area are updated, and the resultant outflows are calculated. The sliders adjust two key unknowns: the seepage coefficient and recharge fraction routed to the reservoir. The resulting simulated reservoir depth (and volume) over time is compared to the observed water level, serving as a calibration target. This application evaluates whether a reasonable calibration can be achieved under the above described conceptualization. If successful, more detailed (e.g. spatially discretized) numerical modelling can follow. If not, the conceptualization must be revisited before more detailed modelling can proceed.
