import numpy as np
import math

# This file contains functions:
# date_to_jd() == converts date to Julian date
# solar_angles() == finds elevation and azimuth angles
# air_mass() == finds air mass
# transmittance() == transmittance based on air mass


def date_to_jd(year, month, day):
    """
    Convert a date to Julian Day.

    Algorithm from 'Practical Astronomy with your Calculator or Spreadsheet', 4th ed., Duffet-Smith and Zwart, 2011.
    Author: Matt Davis
    Website: http://github.com/jiffyclub

    Args:
        year : int. Years preceding 1 A.D. should be 0 or negative. The year before 1 A.D. is 0, 10 B.C. is year -9.
        month : int, Jan = 1, Feb. = 2, etc.
        day : float, may contain fractional part.
        
    Returns:
        jd : float, Julian Day
    """

    if month == 1 or month == 2:
        yearp = year - 1
        monthp = month + 12
    else:
        yearp = year
        monthp = month

    # this checks where we are in relation to October 15, 1582, the beginning
    # of the Gregorian calendar.
    if ((year < 1582) or
            (year == 1582 and month < 10) or
            (year == 1582 and month == 10 and day < 15)):
        # before start of Gregorian calendar
        B = 0
    else:
        # after start of Gregorian calendar
        A = math.trunc(yearp / 100.)
        B = 2 - A + math.trunc(A / 4.)

    if yearp < 0:
        C = math.trunc((365.25 * yearp) - 0.75)
    else:
        C = math.trunc(365.25 * yearp)

    D = math.trunc(30.6001 * (monthp + 1))
    jd = B + C + D + day + 1720994.5

    return jd


def solar_angles(lat, lon, timezone, year, month, day, hour, minute):
    # This function returns a vector containing:
    # the refraction corrected elevation angle (h_corr), the azimuth angle (azimuth), and
    # the julian day (jd)
    # Inputs: (latitude in degrees, longitude in degrees, year, month, day, hour (24-hr clock), minute)
    # All calculations according to NOAA solar calculations

    # Julian day from previously defined function
    julian_day = date_to_jd(year, month, day)

    # Calculate time in 24-hr decimal form
    time = np.add(hour, np.multiply(minute, 1 / 60))

    # Exact Julian day and century based on time during day
    jd = julian_day + time/24 - timezone/24

    jc = np.subtract(jd, 2451545)/36525

    # Geometric parameters
    mean_long_sun = np.mod((280.46646 + jc*(36000.76983 + jc*0.0003032)), 360)

    mean_anom_sun = 357.52911 + jc*(35999.05029 - 0.0001537*jc)

    ecc = 0.016708634 - jc*(0.000042307 + 0.0000001267*jc)

    eq = (np.sin(np.deg2rad(mean_anom_sun)) * (1.914602 - jc * (0.004817 + 0.000014 * jc)) + np.sin(np.deg2rad(2 *
          mean_anom_sun)) * (0.019993 - 0.000101 * jc) + np.sin(np.deg2rad(3 * mean_anom_sun)) * 0.000289)

    true_long_sun = mean_long_sun + eq

    app_long = true_long_sun - 0.00569 - 0.00478*np.sin(np.deg2rad(125.04 - 1934.136 * jc))

    obliq = 23+(26+(21.448 - jc * (46.815 + jc*(0.00059 - jc*0.001813)))/60)/60

    obliq_corr = obliq + 0.00256 * np.cos(np.deg2rad(125.04-1934.136*jc))

    # Declination Angle
    dec = np.rad2deg(np.arcsin(np.sin(np.deg2rad(obliq_corr))*np.sin(np.deg2rad(app_long))))

    var_y = np.tan(np.deg2rad(obliq_corr/2))*np.tan(np.deg2rad(obliq_corr/2))

    # Equation of time
    eot = 4*np.rad2deg(var_y*np.sin(2*np.deg2rad(mean_long_sun))-2*ecc*np.sin(np.deg2rad(mean_anom_sun))+4*ecc*var_y *
                       np.sin(np.deg2rad(mean_anom_sun))*np.cos(2*np.deg2rad(mean_long_sun))-0.5*var_y*var_y *
                       np.sin(4*np.deg2rad(mean_long_sun))-1.25*ecc*ecc*np.sin(2*np.deg2rad(mean_anom_sun)))

    # Solar time in minutes
    true_solar_time = np.mod(time/24*1440 + eot + 4*lon - 60*timezone, 1440)

    # Hour angle
    if true_solar_time/4 < 0:
        hra = true_solar_time/4 + 180
    else:
        hra = true_solar_time/4 - 180

    # Zenith angle
    zenith = np.rad2deg(np.arccos(np.sin(np.deg2rad(lat))*np.sin(np.deg2rad(dec)) + np.cos(np.deg2rad(lat)) *
                                  np.cos(np.deg2rad(dec))*np.cos(np.deg2rad(hra))))

    # Initial uncorrected elevation
    h = 90 - zenith

    # Atmospheric refraction angle
    n = 0
    if 85 <= h < 90:
        n = 0
    elif 5 <= h < 85:
        n = 1/3600*(58.1/np.tan(np.deg2rad(h)) - 0.07/np.power(np.tan(np.deg2rad(h)), 3) +
                    0.000086/np.power(np.tan(np.deg2rad(h)), 5))
    elif -0.575 <= h < 5:
        n = 1/3600*(1735 - 518.2*h + 103.4*np.power(h, 2) - 12.79*np.power(h, 3) + 0.711*np.power(h, 4))
    elif h < -0.575:
        n = 1/3600*(-20.774/np.tan(np.deg2rad(h)))

    # Refraction corrected elevation angle
    h_corr = h + n

    # Solar Azimuth angle (degrees clockwise from N)
    if hra > 0:
        azimuth = np.mod(np.rad2deg(np.arccos(((np.sin(np.deg2rad(lat)) * np.cos(np.deg2rad(zenith))) -
                                               np.sin(np.deg2rad(dec)))/(np.cos(np.deg2rad(lat)) *
                                                                         np.sin(np.deg2rad(zenith)))))+180, 360)
    else:
        azimuth = np.mod(540-np.rad2deg(np.arccos(((np.sin(np.deg2rad(lat))*np.cos(np.deg2rad(zenith))) -
                                                   np.sin(np.deg2rad(dec)))/(np.cos(np.deg2rad(lat)) *
                                                                             np.sin(np.deg2rad(zenith))))), 360)

    # optional debug prints
    """
    print('julian century = {}'.format(jc))
    print('geom mean long sun = {}' .format(mean_long_sun))
    print('geom mean anom = {}' .format(mean_anom_sun))
    print('eot = {}' .format(eot))
    print('true_solar_time = {}'.format(true_solar_time))
    print('hra = {}\n'.format(hra))
    """

    return [h_corr, azimuth, jd]


def air_mass(h):
    # Input is elevation angle h in degrees
    temp = 1229 + np.power(614*np.sin(np.deg2rad(h)), 2)
    m = np.sqrt(temp) - 614*np.sin(np.deg2rad(h))
    return m


def transmittance(m):
    # Input is air mass m
    tau = 0.56*(1/np.power(np.e, 0.65*m) + 1/np.power(np.e, 0.095*m))
    return tau


def irradiance(elevation, julian_day):
    # returns direct normal extraterrestrial solar irradiance and solar irradiance on earth's surface
    # irradiance = measure of instantaneous rate of energy delivered to a surface [W/m^2]
    m = air_mass(elevation)
    tau = transmittance(m)
    # direct normal extraterrestrial solar radiation
    io = 1367*(1 + 0.034*(np.cos(np.deg2rad(360*julian_day/365))))
    # solar radiation on a horizontal plane on earth's surface with atmospheric attenuation
    ioh = io * tau * np.cos(np.deg2rad(90 - elevation))
    return ioh




