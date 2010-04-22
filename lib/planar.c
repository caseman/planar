/***************************************************************************
* Copyright (c) 2010 by Casey Duncan
* All rights reserved.
*
* This software is subject to the provisions of the BSD License
* A copy of the license should accompany this distribution.
* THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
* IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
* FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
****************************************************************************/

double EPSILON = 1e-5;
double EPSILON2 = 1e-5 * 1e-5;

void set_epsilon(double epsilon) {
    EPSILON = epsilon;
    EPSILON2 = epsilon * epsilon;
}

