# do not change the contents of this file as it will be overwiten by updates
# make custom changes in <machinename>_connections.hal

#***** PLASMAC COMPONENT *****
loadrt  plasmac
addf    plasmac  servo-thread

# QTPLASMAC/MONOKROM-PLASMA TOOLCHANGE PASSTHROUGH
net tool-number <= iocontrol.0.tool-prep-number
net tool-change-loopback iocontrol.0.tool-change => iocontrol.0.tool-changed
net tool-prepare-loopback iocontrol.0.tool-prepare => iocontrol.0.tool-prepared



# INPUTS
# ---PLASMAC COMPONENT INPUTS---
net plasmac:arc-ok               db_arc-ok.out               =>  plasmac.arc-ok-in
net plasmac:axis-position        joint.${z-axis}.pos-fb      =>  plasmac.axis-z-position
net plasmac:axis-x-position      axis.x.pos-cmd              =>  plasmac.axis-x-position
net plasmac:axis-y-position      axis.y.pos-cmd              =>  plasmac.axis-y-position
net plasmac:breakaway-switch-out db_breakaway.out            =>  plasmac.breakaway
net plasmac:current-velocity     motion.current-vel          =>  plasmac.current-velocity
net plasmac:cutting-start        spindle.0.on                =>  plasmac.cutting-start
net plasmac:feed-override        halui.feed-override.value   =>  plasmac.feed-override
net plasmac:feed-reduction       motion.analog-out-03        =>  plasmac.feed-reduction
net plasmac:float-switch-out     db_float.out                =>  plasmac.float-switch
net plasmac:ignore-arc-ok-0      motion.digital-out-01       =>  plasmac.ignore-arc-ok-0
net plasmac:motion-type          motion.motion-type          =>  plasmac.motion-type
net plasmac:offsets-active       motion.eoffset-active       =>  plasmac.offsets-active
net plasmac:ohmic-probe-out      db_ohmic.out                =>  plasmac.ohmic-probe
net plasmac:program-is-idle      halui.program.is-idle       =>  plasmac.program-is-idle
net plasmac:program-is-paused    halui.program.is-paused     =>  plasmac.program-is-paused
net plasmac:program-is-running   halui.program.is-running    =>  plasmac.program-is-running
net plasmac:requested-velocity   motion.requested-vel        =>  plasmac.requested-velocity
net plasmac:scribe-start         spindle.1.on                =>  plasmac.scribe-start
net plasmac:spotting-start       spindle.2.on                =>  plasmac.spotting-start
net plasmac:thc-disable          motion.digital-out-02       =>  plasmac.thc-disable
net plasmac:torch-off            motion.digital-out-03       =>  plasmac.torch-off
net plasmac:units-per-mm         halui.machine.units-per-mm  =>  plasmac.units-per-mm
net plasmac:x-offset-current     axis.x.eoffset              =>  plasmac.x-offset-current
net plasmac:y-offset-current     axis.y.eoffset              =>  plasmac.y-offset-current
net plasmac:z-offset-current     axis.z.eoffset              =>  plasmac.z-offset-current


net plasmac:cornerlock-enable                                    plasmac.cornerlock-enable
net plasmac:cornerlock-threshold                                 plasmac.cornerlock-threshold
net plasmac:cut-feed-rate                                        plasmac.cut-feed-rate
net plasmac:cut-height                                           plasmac.cut-height
net plasmac:cut-length                                           plasmac.cut-length
net plasmac:cut-time                                             plasmac.cut-time
net plasmac:cut-volts                                            plasmac.cut-volts
net plasmac:float-switch-travel                                  plasmac.float-switch-travel
net plasmac:height-override                                      plasmac.height-override
net plasmac:height-per-volt                                      plasmac.height-per-volt
net plasmac:ignore-arc-ok-1                                      plasmac.ignore-arc-ok-1
net plasmac:kerfcross-enable                                     plasmac.kerfcross-enable
net plasmac:kerfcross-override                                   plasmac.kerfcross-override
net plasmac:mesh-enable                                          plasmac.mesh-enable
net plasmac:ohmic-max-attempts                                   plasmac.ohmic-max-attempts
net plasmac:ohmic-probe-enable                                   plasmac.ohmic-probe-enable
net plasmac:ohmic-probe-offset                                   plasmac.ohmic-probe-offset
net plasmac:pause-at-end                                         plasmac.pause-at-end
net plasmac:pid-d-gain                                           plasmac.pid-d-gain
net plasmac:pid-i-gain                                           plasmac.pid-i-gain
net plasmac:pid-p-gain                                           plasmac.pid-p-gain
net plasmac:pierce-delay                                         plasmac.pierce-delay
net plasmac:pierce-height                                        plasmac.pierce-height
net plasmac:probe-feed-rate                                      plasmac.probe-feed-rate
net plasmac:probe-start-height                                   plasmac.probe-start-height
net plasmac:puddle-jump-delay                                    plasmac.puddle-jump-delay
net plasmac:puddle-jump-height                                   plasmac.puddle-jump-height
net plasmac:restart-delay                                        plasmac.restart-delay
net plasmac:safe-height                                          plasmac.safe-height
net plasmac:scribe-arm-delay                                     plasmac.scribe-arm-delay
net plasmac:scribe-on-delay                                      plasmac.scribe-on-delay
net plasmac:setup-feed-rate                                      plasmac.setup-feed-rate
net plasmac:skip-ihs-distance                                    plasmac.skip-ihs-distance
net plasmac:spotting-threshold                                   plasmac.spotting-threshold
net plasmac:spotting-time                                        plasmac.spotting-time
net plasmac:thc-delay                                            plasmac.thc-delay
net plasmac:thc-enable                                           plasmac.thc-enable
net plasmac:thc-feed-rate                                        plasmac.thc-feed-rate
net plasmac:thc-threshold                                        plasmac.thc-threshold
net plasmac:torch-enable                                         plasmac.torch-enable
net plasmac:use-auto-volts                                       plasmac.use-auto-volts



# use existing machine-is-on signal from pncconf if it exists
if {[hal list sig machine-is-on] != {}} {
    net machine-is-on                                           =>  plasmac.machine-is-on
} else {
    net machine-is-on               halui.machine.is-on         =>  plasmac.machine-is-on
}

# v0.173 and later use dbounce in lieu of debounce
if [info exists ::PLASMAC(DBOUNCE)] {
    net plasmac:float-switch-out        db_float.out            =>  plasmac.float-switch
    net plasmac:breakaway-switch-out    db_breakaway.out        =>  plasmac.breakaway
    net plasmac:ohmic-probe-out         db_ohmic.out            =>  plasmac.ohmic-probe
    net plasmac:arc-ok                  db_arc-ok.out           =>  plasmac.arc-ok-in
} else {
    net plasmac:float-switch-out        debounce.0.0.out        =>  plasmac.float-switch
    net plasmac:breakaway-switch-out    debounce.0.1.out        =>  plasmac.breakaway
    net plasmac:ohmic-probe-out         debounce.0.2.out        =>  plasmac.ohmic-probe
}

# OUTPUTS
net plasmac:adaptive-feed           plasmac.adaptive-feed       =>  motion.adaptive-feed
net plasmac:cutting-stop            halui.spindle.0.stop        =>  plasmac.cutting-stop
net plasmac:feed-hold               plasmac.feed-hold           =>  motion.feed-hold
net plasmac:offset-scale            plasmac.offset-scale        =>  axis.x.eoffset-scale axis.y.eoffset-scale axis.z.eoffset-scale
net plasmac:program-pause           plasmac.program-pause       =>  halui.program.pause
net plasmac:program-resume          plasmac.program-resume      =>  halui.program.resume
net plasmac:program-run             plasmac.program-run         =>  halui.program.run
net plasmac:program-stop            plasmac.program-stop        =>  halui.program.stop
net plasmac:torch-on                plasmac.torch-on
net plasmac:x-offset-counts         plasmac.x-offset-counts     =>  axis.x.eoffset-counts
net plasmac:y-offset-counts         plasmac.y-offset-counts     =>  axis.y.eoffset-counts
net plasmac:xy-offset-enable        plasmac.xy-offset-enable    =>  axis.x.eoffset-enable axis.y.eoffset-enable
net plasmac:z-offset-counts         plasmac.z-offset-counts     =>  axis.z.eoffset-counts
net plasmac:z-offset-enable         plasmac.z-offset-enable     =>  axis.z.eoffset-enable
net plasmac:consumable-changing     plasmac.consumable-changing
net plasmac:cornerlock-is-locked    plasmac.cornerlock-is-locked
net plasmac:kerfcross-is-locked     plasmac.kerfcross-is-locked
net plasmac:led-down                plasmac.led-down
net plasmac:led-up                  plasmac.led-up
net plasmac:pierce-count            plasmac.pierce-count
net plasmac:probe-test-error        plasmac.probe-test-error
net plasmac:state                   plasmac.state-out
net plasmac:thc-active              plasmac.thc-active
net plasmac:thc-enable              plasmac.thc-enabled
net plasmac:z-height                plasmac.z-height



# multiple spindles
if [info exists ::TRAJ(SPINDLES)] {
    set num_spindles [lindex $::TRAJ(SPINDLES) 0]
    if {$num_spindles > 1} {net plasmac:scribe-start spindle.1.on => plasmac.scribe-start}
    if {$num_spindles > 2} {net plasmac:spotting-start spindle.2.on => plasmac.spotting-start}
}

# powermax serial communications
if [info exists ::PLASMAC(PM_PORT)] {loadusr -Wn pmx485 pmx485 [lindex $::PLASMAC(PM_PORT) 0]}
