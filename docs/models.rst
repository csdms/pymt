.. _available_models:

Available Components
====================

Data Components
---------------

The following table lists the data components currently
available through *pymt*.

==========  ===================================================================================================================
GeoTiff     Access data and metadata from a GeoTIFF file, through either a local filepath or a remote URL.
GridMET     Fetch and cache gridMET meteorological data.
NWIS        Download the National Water Information System (Nwis) time series datasets.
NWM         Download the National Water Model datasets.
SoilGrids   Download the soil property datasets from the SoilGrids system.
Topography  Fetch and cache NASA Shuttle Radar Topography Mission (SRTM) land elevation data using the OpenTopography REST API.
==========  ===================================================================================================================

Model Components
----------------

The following table lists the model components currently available through
*pymt*.


================================  =================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================
..                                Summary
================================  =================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================
Avulsion                          Avulsion dictates the movement of rivermouths along a coastline by modeling the changes of river channel angles through the floodplain as a stochastic random walk process.
Cem                               The Coastline Evolution Model addresses predominately sandy, wave-dominated coastlines on time scales ranging from years to millenia and on spatial scales ranging from kilometers to hundreds of kilometers. CEM simulates planview coastline evolution due to wave-driven alongshore sediment transport. This model can incorporate river influence and transport fluvial sediment from one or more point sources along the coastline.

                                  |binder-Cem|
Child                             CHILD computes the time evolution of a topographic surface z(x,y,t) by fluvial and hillslope erosion and sediment transport.

                                  |binder-Child|
ECSimpleSnow                      ECSimpleSnow was orginally developed by Ross Brown and Bruce Brasnett in Environment Canada (EC). It is an empirical algorithm to melt snow according to the surface temperature and increase in snow depth according to the precipitation that has fallen since the last analysis time. It is a semi-empirical temperature index model. It provides a quick and acceptable answer when you only have very limited inputs. The one deficiency of the model is that it does not take account of the heat budget of the snowpack which means it will melt snow too quickly in the spring.

                                  |binder-ECSimpleSnow|
ExponentialWeatherer              Exponential weathering of bedrock on hillslopes.  Uses exponential soil
                                  production function in the style of Ahnert (1976).
Flexure                           Simulate lithospheric flexure.
FlowAccumulator                   Component to accumulate flow and calculate drainage area.  This is
                                  accomplished by first finding flow directions by a user-specified
                                  method and then calculating the drainage area and discharge.
                                  Optionally, spatially variable runoff can be set either by the
                                  model grid field 'water__unit_flux_in'.
FlowDirectorD8                    Single-path (steepest direction) flow direction finding on raster grids by the D8 method. This method considers flow on all eight links such that flow is possible on orthogonal and on diagonal links.
FlowDirectorDINF                  Directs flow by the D infinity method (Tarboton, 1997). Each node is
                                  assigned two flow directions, toward the two neighboring nodes that are on
                                  the steepest subtriangle. Partitioning of flow is done based on the aspect
                                  of the subtriangle.
FlowDirectorSteepest              Find the steepest single-path steepest descent flow
                                  directions. It is equivalent to D4 method in the special case of a raster grid
                                  in that it does not consider diagonal links between nodes. For that capability,
                                  use FlowDirectorD8.
FlowRouter                        Single-path (steepest direction) flow routing, and calculates flow directions, drainage area, and (optionally) discharge.
FrostNumber                       From Nelson and Outcalt (1987), the 'frost number', a dimensionless ratio defined by manipulation of either freezing and thawing degree-day sums or frost and thaw penetration depths, can be used to define an unambiguous latitudinal zonation of permafrost continuity. The index is computed using several variables influencing the depth of frost and thaw penetration, and can be related mathematically to the existence and continuity of permafrost. Although the frost number is a useful device for portraying the distribution of contemporary permafrost at continental scales, it is not capable of detecting relict permafrost and should not be mapped over small areas unless numerous climate stations are located in the region of interest.

                                  |binder-FrostNumber|
GIPL                              GIPL (Geophysical Institute Permafrost Laboratory) is an implicit
                                  finite difference one-dimensional heat flow numerical model. The
                                  model uses a fine vertical resolution grid which preserves the
                                  latent-heat effects in the phase transition zone, even under
                                  conditions of rapid or abrupt changes in the temperature fields. It
                                  includes upper boundary condition (usually air temperature),
                                  constant geothermal heat flux at the lower boundary (typically from
                                  500 to 1000 m) and initial temperature distribution with depth. The
                                  other inputs are precipitation, prescribed water content and thermal
                                  properties of the multilayered soil column. As an output the model
                                  produces temperature distributions at different depths, active layer
                                  thickness and calculates time of freeze up. The results include
                                  temperatures at different depths and active layer thickness,
                                  freeze-up days.


                                  |binder-GIPL|
Hydrotrend                        Climate-driven hydrological water balance and transport model that simulates water discharge and sediment load at a river outlet. HydroTrend simulates water and sediment fluxes at a daily timescale based on drainage basin characteristics and climate. HydroTrend can provide this river flux information to other components like CEM and Sedflux2D or Sedflux3D

                                  |binder-Hydrotrend|
Ku                                The Kudryavtsev et al. (1974), or Ku model, presents an approximate solution of the Stefan problem. The model provides a steady-state solution under the assumption of sinusoidal air temperature forcing. It considers snow, vegetation, and soil layers as thermal damping to variation of air temperature. The layer of soil is considered to be a homogeneous column with different thermal properties in the frozen and thawed states. The main outputs are annual maximum frozen/thaw depth and mean annual temperature at the top of permafrost (or at the base of the active layer). It can be applied over a wide variety of climatic conditions.

                                  |binder-Ku|
LinearDiffuser                    2D diffusion using an explicit finite-volume method.
OverlandFlow                      Simulate overland flow using de Almeida approximations.  Landlab component
                                  that simulates overland flow using the de Almeida et al., 2012
                                  approximations of the 1D shallow water equations to be used for
                                  2D flood inundation modeling.  This component calculates discharge,
                                  depth and shear stress after some precipitation event across any raster grid.
Plume                             Plume simulates the sediment transport and deposition of single-grain size sediment from a river mouth entering into a marine basin by creating a turbulent jet. The model calculates a steady-state hypopycnal plume as a result of river water and sediment discharge based on simplified advection-diffusion equations. The model allows for plume deflection due to systematic coastal currents or Coriolis force
Rafem                             The River Avulsion and Floodplain Evolution Model (RAFEM) is a cellular model that simulates river and floodplain morphodynamics over large space and timescales. Cell size is larger than the channel belt width, and natural levees, which maintain a bankfull elevation above the channel bed, exist within a river cell. The river course is determined using a steepest-descent methodology, and erosion and deposition along the river profile are modeled as a linear diffusive process. An avulsion occurs when the riverbed becomes super-elevated relative to the surrounding floodplain, but only if the new steepest-descent path to sea level is shorter than the prior river course. If the new path to sea level is not shorter, then a crevasse splay is deposited in the adjacent river cells. The model has been designed to couple with the Coastline Evolution Model through the CSDMS Basic Model Interface.
Sedflux3D                         Sedflux3D is a basin filling stratigraphic model. Sedflux3d simulates long-term marine sediment transport and accumulation into a three-dimensional basin over time scales of tens of thousands of years. It simulates the dynamics of strata formation of continental margins based on distribution of river plumes and tectonics.

                                  |binder-Sedflux3D|
SoilMoisture                      Landlab component that simulates root-zone average soil moisture at each
                                  cell using inputs of potential evapotranspiration, live leaf area index,
                                  and vegetation cover.
StreamPowerEroder                 A simple, explicit implementation of a stream power algorithm.
Subside                           The model is used to simulate the lithospheric load changes as the model evolves. Depending upon how the load distribution develops, this flexure can result in the basin uplifting or subsiding (or both). The pattern of subsidence in time and space largely determines the gross geometry of time-bounded units because it controls the rate at which space is created for sedimentation.

                                  |binder-Subside|
TransportLengthHillslopeDiffuser  Hillslope diffusion component in the style of Carretier et al.
                                  (2016, ESurf), and Davy and Lague (2009)
Vegetation                        Landlab component that simulates net primary productivity, biomass
                                  and leaf area index at each cell based on inputs of root-zone
                                  average soil moisture.

                                  Zhou, X., Istanbulluoglu, E., & Vivoni, E. R. (2013). Modeling the
                                  ecohydrological role of aspect controlled radiation on tree grass shrub
                                  coexistence in a semiarid climate. Water Resources Research,
                                  49(5), 2872-2895.
Waves                             Generates a shallow-water wave climate for a longshore transport module based on a user-defined distribution.

                                  |binder-Waves|
================================  =================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================

.. |binder-ECSimpleSnow| image:: https://mybinder.org/badge_logo.svg
    :target: https://mybinder.org/v2/gh/csdms/pymt.git/master?filepath=notebooks%2Fecsimplesnow.ipynb


.. |binder-Cem| image:: https://mybinder.org/badge_logo.svg
    :target: https://mybinder.org/v2/gh/csdms/pymt.git/master?filepath=notebooks%2Fcem.ipynb


.. |binder-Waves| image:: https://mybinder.org/badge_logo.svg
    :target: https://mybinder.org/v2/gh/csdms/pymt.git/master?filepath=notebooks%2Fcem_and_waves.ipynb


.. |binder-GIPL| image:: https://mybinder.org/badge_logo.svg
    :target: https://mybinder.org/v2/gh/csdms/pymt.git/master?filepath=notebooks%2Fgipl.ipynb


.. |binder-Child| image:: https://mybinder.org/badge_logo.svg
    :target: https://mybinder.org/v2/gh/csdms/pymt.git/master?filepath=notebooks%2Fchild.ipynb


.. |binder-Sedflux3D| image:: https://mybinder.org/badge_logo.svg
    :target: https://mybinder.org/v2/gh/csdms/pymt.git/master?filepath=notebooks%2Fsedflux3d.ipynb


.. |binder-FrostNumber| image:: https://mybinder.org/badge_logo.svg
    :target: https://mybinder.org/v2/gh/csdms/pymt.git/master?filepath=notebooks%2Ffrost_number.ipynb


.. |binder-Hydrotrend| image:: https://mybinder.org/badge_logo.svg
    :target: https://mybinder.org/v2/gh/csdms/pymt.git/master?filepath=notebooks%2Fhydrotrend.ipynb


.. |binder-Subside| image:: https://mybinder.org/badge_logo.svg
    :target: https://mybinder.org/v2/gh/csdms/pymt.git/master?filepath=notebooks%2Fsubside.ipynb


.. |binder-Ku| image:: https://mybinder.org/badge_logo.svg
    :target: https://mybinder.org/v2/gh/csdms/pymt.git/master?filepath=notebooks%2Fku.ipynb

