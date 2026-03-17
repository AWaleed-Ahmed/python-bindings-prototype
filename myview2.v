#!/bin/sh
rt -M \
 -o myview2.v.pix\
 $*\
 'test_stage10.g'\
 's1' 's2' 'comb1' '_GLOBAL' \
 2>> myview2.v.log\
 <<EOF
viewsize 8.00000000000000e+00;
orientation 2.48097349045873e-01 4.76590573266048e-01 7.48097349045873e-01 3.89434830518390e-01;
eye_pt 1.02870498707573e+01 7.20306986544349e+00 5.85597041233067e+00;
start 0; clean;
end;

EOF
