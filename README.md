# Solar Array Power Calculator

This project was done for the University of Toronto Blue Sky Solar Racing Club. The goals were to **model the direction and intensity of the vector of the Sun's rays** and to **find the total power produced by the solar panels** at a point on Earth defined by the longitude and latitude at a specified time and date.

To model the sun, equations are derived from public resources, namely [PVEducation](http://www.pveducation.org/) and [NOAA Sun Calculator](https://www.esrl.noaa.gov/gmd/grad/solcalc/). These equations are used to calculate the Sun ray vector, which is then cross-multiplied with the 3D mesh normal vectors of the car to find the power produced. 
