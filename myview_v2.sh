#!/bin/sh
rt -M \
 -o myview_v2.pix\
 $*\
 'test_stage10_render.g'\
 \
 2>> myview_v2.log\
 <<EOF
viewsize 1.00000000000000e+01;
orientation 2.48097349045873e-01 4.76590573266048e-01 7.48097349045873e-01 3.89434830518390e-01;
eye_pt -nan -nan -nan;
start 0; clean;
end;

EOF
