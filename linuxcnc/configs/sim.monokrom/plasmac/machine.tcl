# GENERIC HAL FILE FOR QTPLASMAC SIM CONFIGS

# ---SET CONSTANTS---
set numJoints $::KINS(JOINTS)
set z-axis [string first "z" [string tolower $::TRAJ(COORDINATES)]]

# ---COMPONENTS---
loadrt $::KINS(KINEMATICS)
loadrt $::EMCMOT(EMCMOT) servo_period_nsec=$::EMCMOT(SERVO_PERIOD) num_joints=$numJoints num_spindles=$::TRAJ(SPINDLES) num_dio=4

for {set jnum 0} {$jnum < $numJoints} {incr jnum} {
    loadrt pid names=sim:${jnum}_pid
    loadrt mux2 names=sim:${jnum}_mux
    loadrt ddt names=sim:${jnum}_vel,sim:${jnum}_accel
    loadrt sim_home_switch names=sim:${jnum}_switch
}
loadrt hypot names=sim:hyp_xy,sim:hyp_xyz

# ---THREAD LINKS---
addf motion-command-handler servo-thread
addf motion-controller servo-thread
for {set jnum 0} {$jnum < $numJoints} {incr jnum} {
    addf sim:${jnum}_pid.do-pid-calcs servo-thread
    addf sim:${jnum}_mux servo-thread
    addf sim:${jnum}_vel servo-thread
    addf sim:${jnum}_accel servo-thread
}
for {set jnum 0} {$jnum < $numJoints} {incr jnum} {
    addf sim:${jnum}_switch servo-thread
}

# ---SETP COMMANDS FOR UNCONNECTED INPUT PINS---
for {set jnum 0} {$jnum < $numJoints} {incr jnum} {
    setp sim:${jnum}_pid.Pgain 0
    setp sim:${jnum}_pid.Dgain 0
    setp sim:${jnum}_pid.Igain 0
    setp sim:${jnum}_pid.FF0 1.0
    setp sim:${jnum}_pid.FF1 0
    setp sim:${jnum}_pid.FF2 0
}

# ---MACHINE NET CONNECTIONS---
for {set jnum 0} {$jnum < $numJoints} {incr jnum} {
    net sim:j${jnum}-acc sim:${jnum}_accel.out
    net sim:j${jnum}-enable joint.${jnum}.amp-enable-out => sim:${jnum}_pid.enable
    net sim:j${jnum}-homesw sim:${jnum}_switch.home-sw => joint.${jnum}.home-sw-in
    net sim:j${jnum}-on-pos sim:${jnum}_pid.output => sim:${jnum}_mux.in1
    net sim:j${jnum}-pos-cmd joint.${jnum}.motor-pos-cmd => sim:${jnum}_pid.command
    net sim:j${jnum}-pos-fb sim:${jnum}_mux.out => sim:${jnum}_mux.in0 sim:${jnum}_switch.cur-pos sim:${jnum}_vel.in joint.${jnum}.motor-pos-fb
    net sim:j${jnum}-vel sim:${jnum}_vel.out => sim:${jnum}_accel.in
}
net sim:xy-vel sim:hyp_xy.out
net sim:xyz-vel sim:hyp_xyz.out
net sim:enable motion.motion-enabled
for {set jnum 0} {$jnum < $numJoints} {incr jnum} {
    net sim:enable sim:${jnum}_mux.sel
}
foreach {x y z } {0 0 0 } {}
for {set jnum 0} {$jnum < $numJoints} {incr jnum} {
    if {[string index $::TRAJ(COORDINATES) $jnum] == "X"} {
        if {$x == 0} {
            incr x
            net sim:j${jnum}-vel => sim:hyp_xy.in0 sim:hyp_xyz.in0
        }
    } elseif {[string index $::TRAJ(COORDINATES) $jnum] == "Y"} {
        if {$y == 0} {
            incr y
            net sim:j${jnum}-vel => sim:hyp_xy.in1 sim:hyp_xyz.in1
        }
    } elseif {[string index $::TRAJ(COORDINATES) $jnum] == "Z"} {
        if {$z == 0} {
            incr z
            net sim:j${jnum}-vel => sim:hyp_xyz.in2
        }
    }
}


# Standard estop shape
# loadrt estop_latch names=ui_estop
# addf ui_estop servo-thread
# net estop:ok-out    ui_estop.ok-out => iocontrol.0.emc-enable-in

# estop loopback
net estop-loop iocontrol.0.user-enable-out iocontrol.0.emc-enable-in

# QTPLASMAC SIM ESTOP HANDLING - these are here to keep
# qtplasmac-sim happy
loadrt or2 names=estop_or
addf estop_or servo-thread
