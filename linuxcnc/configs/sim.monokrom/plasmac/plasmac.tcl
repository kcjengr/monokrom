# do not change the contents of this file as it will be overwiten by updates
# make custom changes in <machinename>_connections.hal


# ---SET CONSTANTS---
if {![info exists numJoints]} {
    set numJoints $::KINS(JOINTS)
}
if {![info exists z-axis]} {
    set z-axis [string first "z" [string tolower $::TRAJ(COORDINATES)]]
}

#***** PLASMAC COMPONENT *****
loadrt  plasmac
addf    plasmac  servo-thread

#***** All Homed logic *****
loadrt logic names=allhomed personality=0x10${numJoints}
addf allhomed servo-thread
for {set jnum 0} {$jnum < $numJoints} {incr jnum} {
    net allhomed:in-${jnum}    halui.joint.${jnum}.is-homed  => allhomed.in-[format "%02u" $jnum]
}

# Set Plasmac Mode
setp plasmac.mode 1

# Debug
setp plasmac.debug-print 1

# QTPLASMAC/MONOKROM-PLASMA TOOLCHANGE PASSTHROUGH
net tool-number <= iocontrol.0.tool-prep-number
net tool-change-loopback iocontrol.0.tool-change => iocontrol.0.tool-changed
net tool-prepare-loopback iocontrol.0.tool-prepare => iocontrol.0.tool-prepared



# INPUTS
# ---PLASMAC COMPONENT INPUTS---
#net plasmac:arc-ok               db_arc-ok.out               =>  plasmac.arc-ok-in
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
net plasmac:machine-is-homed     allhomed.and                =>  plasmac.homed
net plasmac:feed-upm             motion.feed-upm             =>  plasmac.feed-upm


# use existing machine-is-on signal from pncconf if it exists
if {[hal list sig machine-is-on] != {}} {
    net machine-is-on                                           =>  plasmac.machine-is-on
} else {
    net machine-is-on               halui.machine.is-on         =>  plasmac.machine-is-on
}

# v0.173 and later use dbounce in lieu of debounce
#if [info exists ::PLASMAC(DBOUNCE)] {
net plasmac:float-switch-out        db_float.out            =>  plasmac.float-switch
net plasmac:breakaway-switch-out    db_breakaway.out        =>  plasmac.breakaway
net plasmac:ohmic-probe-out         db_ohmic.out            =>  plasmac.ohmic-probe
net plasmac:arc-ok                  db_arc-ok.out           =>  plasmac.arc-ok-in
#} else {
#    net plasmac:float-switch-out        debounce.0.0.out        =>  plasmac.float-switch
#    net plasmac:breakaway-switch-out    debounce.0.1.out        =>  plasmac.breakaway
#    net plasmac:ohmic-probe-out         debounce.0.2.out        =>  plasmac.ohmic-probe
#}

# OUTPUTS
net plasmac:adaptive-feed           plasmac.adaptive-feed       =>  motion.adaptive-feed
net plasmac:cutting-stop            halui.spindle.0.stop        =>  plasmac.cutting-stop
net plasmac:feed-hold               plasmac.feed-hold           =>  motion.feed-hold
net plasmac:offset-scale            plasmac.offset-scale        =>  axis.x.eoffset-scale axis.y.eoffset-scale axis.z.eoffset-scale
net plasmac:program-pause           plasmac.program-pause       =>  halui.program.pause
net plasmac:program-resume          plasmac.program-resume      =>  halui.program.resume
net plasmac:program-run             plasmac.program-run         =>  halui.program.run
net plasmac:program-stop            plasmac.program-stop        =>  halui.program.stop
#net plasmac:torch-on                plasmac.torch-on
net plasmac:x-offset-counts         plasmac.x-offset-counts     =>  axis.x.eoffset-counts
net plasmac:y-offset-counts         plasmac.y-offset-counts     =>  axis.y.eoffset-counts
net plasmac:xy-offset-enable        plasmac.xy-offset-enable    =>  axis.x.eoffset-enable axis.y.eoffset-enable
net plasmac:z-offset-counts         plasmac.z-offset-counts     =>  axis.z.eoffset-counts
net plasmac:z-offset-enable         plasmac.z-offset-enable     =>  axis.z.eoffset-enable




# multiple spindles
if [info exists ::TRAJ(SPINDLES)] {
    set num_spindles [lindex $::TRAJ(SPINDLES) 0]
    if {$num_spindles > 1} {net plasmac:scribe-start spindle.1.on => plasmac.scribe-start}
    if {$num_spindles > 2} {net plasmac:spotting-start spindle.2.on => plasmac.spotting-start}
}

# powermax serial communications
if [info exists ::PLASMAC(PM_PORT)] {loadusr -Wn pmx485 pmx485 [lindex $::PLASMAC(PM_PORT) 0]}
