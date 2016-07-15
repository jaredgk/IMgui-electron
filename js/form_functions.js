/*global alert, $, jQuery, FileReader*/

/*IMgui 2016- Jared Knoblauch, Arun Sethuraman, and Jody Hey*/

//"use strict";

//var remote = require('remote');
var windowManager = require('electron').remote.require('electron-window-manager');
var ipcRenderer = require('electron').ipcRenderer;
var remote = require('electron').remote;
var pwd = remote.getGlobal('sharedObj').pwd;
var homedir = remote.getGlobal('sharedObj').homedir;

function getName(el) {
    var pref = '';
    if($('#working-dir').val().length !== 0) {
        pref = $('#working-dir').val().replace(/[ ]/g,'%20');
        if(pref[pref.length-1] !== sep) { pref += sep; }
    }
    var filename = $(el).val().replace(/[ ]/g,'%20');
    if(pref.length !== 0) { filename = pref + filename; }
    if(filename[0] == '~') {
        var t = filename.replace('~',homedir.replace(/[ ]/,'%20'));
        filename = t;
    }
    return filename;
}

ipcRenderer.on('test_response',function(e,data) {
    console.log(data);
});
    

//Creates command line for IMa2 from the input form
function printParams() {
    var c = '-c'; var j = '-j'; var p = '-p'; var r = '-r'; var cmdline = ''; var f = '-f'; var b = '-b'; var d = '-d'; var g = '-g'; var hf = '-hf'; var hn = '-hn'; var hk = '-hk'; var ha = '-ha'; var hb = '-hb'; var i = '-i'; var l = '-l'; var m = '-m'; var o = '-o'; var q = '-q'; var s = '-s'; var t = '-t'; var u = '-u'; var v = '-v'; var w = '-w'; var y = '-y'; var z = '-z'; var radios = document.getElementById('heating-type'); var ii;
    if (document.getElementById('burn').value && ($('input[name="run-mode"]:checked').val() === 'm')) { b += document.getElementById('burn').value.toString(); }
    if (document.getElementById('gene-save').value && ($('input[name="run-mode"]:checked').val() === 'm')) { d += document.getElementById('gene-save').value.toString(); }
    if (document.getElementById('run-time').value) { l += document.getElementById('run-time').value.toString(); }
    if (document.getElementById('seed').value) { s += document.getElementById('seed').value.toString(); }
    if (document.getElementById('out-step').value && ($('input[name="run-mode"]:checked').val() === 'm')) { z += document.getElementById('out-step').value.toString(); }
    if (document.getElementById('mpv').value) { m += document.getElementById('mpv').value.toString(); }
    if (document.getElementById('mps').value) { q += document.getElementById('mps').value.toString(); }
    if (document.getElementById('mtps').value) { t += document.getElementById('mtps').value.toString(); }
    if (document.getElementById('outtag').value) { o += getName('#outtag'); }
    if (document.getElementById('infile').value) { i += getName('#infile'); }
    if (document.getElementById('c1').checked) { c += '0'; }
    if (document.getElementById('c2').checked) { c += '1'; }
    if (document.getElementById('c3').checked && ($('input[name="run-mode"]:checked').val() === 'l')) {
        c += '2';
        w += getName('#nestedf');
    }
    if (document.getElementById('c4').checked) {
        c += '3';
        g += getName('#paramf');
    }
    hf += $('input[name="heating-type"]:checked').val();
    if (document.getElementById('burn-noc').value) { hn += document.getElementById('burn-noc').value.toString(); }
    if (document.getElementById('burn-swap').value) { hk += document.getElementById('burn-swap').value.toString(); }
    if (document.getElementById('burn-first').value) { ha += document.getElementById('burn-first').value.toString(); }
    if (document.getElementById('burn-second').value) { hb += document.getElementById('burn-second').value.toString(); }
    if (document.getElementById('j1').checked) { j += '1'; }
    if (document.getElementById('j2').checked) { j += '2'; }
    if (document.getElementById('j3').checked) { j += '3'; }
    if (document.getElementById('j4').checked) { j += '4'; }
    if (document.getElementById('j5').checked) { j += '5'; }
    if (document.getElementById('j6').checked) { j += '6'; }
    if (document.getElementById('j7').checked) { j += '7'; }
    if (document.getElementById('j8').checked) { j += '8'; }
    if (document.getElementById('j9').checked) { j += '9'; }
    if (document.getElementById('p1').checked) { p += '0'; }
    if (document.getElementById('p2').checked) { p += '1'; }
    if (document.getElementById('p3').checked && ($('input[name="run-mode"]:checked').val() === 'm')) { p += '2'; }
    if (document.getElementById('p4').checked) {
        p += '3';
        u += document.getElementById('gen-time').value.toString();
        y += document.getElementById('mut-rate').value.toString();
    }
    if (document.getElementById('p5').checked) { p += '4'; }
    if (document.getElementById('p6').checked) { p += '5'; }
    if (document.getElementById('p7').checked) { p += '6'; }
    if (document.getElementById('p8').checked && ($('input[name="run-mode"]:checked').val() === 'm')) { p += '7'; }
    if (document.getElementById('p9').checked && ($('input[name="run-mode"]:checked').val() === 'm')) { p += '8'; }
    if (document.getElementById('r1').checked && ($('input[name="run-mode"]:checked').val() === 'l')) {
        r += '0';
        v += getName('#titag');
    }
    if (document.getElementById('r2').checked) { r += '1'; }
    if (document.getElementById('r3').checked && ($('input[name="run-mode"]:checked').val() === 'm')) { r += '2'; }
    if (document.getElementById('r4').checked) {
        r += '3';
        f += getName('#mcftag');
    }
    if (document.getElementById('r5').checked) { r += '4'; }
    if (document.getElementById('r6').checked) { r += '5'; }
    if (b.length > 2) { cmdline += (b + ' '); }
    if (c.length > 2) { cmdline += (c + ' '); }
    if (d.length > 2) { cmdline += (d + ' '); }
    if (f.length > 2) { cmdline += (f + ' '); }
    if (g.length > 2) { cmdline += (g + ' '); }
    if (document.getElementById('mc-check').checked && ($('input[name="run-mode"]:checked').val() === 'm')) {
        if (hf.length > 3) { cmdline += (hf + ' '); }
        if (hn.length > 3) { cmdline += (hn + ' '); }
        if (hk.length > 3) { cmdline += (hk + ' '); }
        if (ha.length > 3) { cmdline += (ha + ' '); }
        if (hb.length > 3) { cmdline += (hb + ' '); }
    }
    if (i.length > 2) { cmdline += (i + ' '); }
    if (l.length > 2) { cmdline += (l + ' '); }
    if (m.length > 2) { cmdline += (m + ' '); }
    if (o.length > 2) { cmdline += (o + ' '); }
    if (q.length > 2) { cmdline += (q + ' '); }
    if (s.length > 2) { cmdline += (s + ' '); }
    if (t.length > 2) { cmdline += (t + ' '); }
    if (u.length > 2) { cmdline += (u + ' '); }
    if (v.length > 2) { cmdline += (v + ' '); }
    if (w.length > 2) { cmdline += (w + ' '); }
    if (y.length > 2) { cmdline += (y + ' '); }
    if (z.length > 2) { cmdline += (z + ' '); }
    if (j.length > 2) { cmdline += (j + ' '); }
    if (p.length > 2) { cmdline += (p + ' '); }
    if (r.length > 2) { cmdline += (r + ' '); }
    return cmdline;
}


//Validates that if a certain check option requires a filename it is provided
function v_check_line(check, line) {
    if (check.checked && line.length === 0) {
        return 0;
    }
    return 1;
}

//Displays error field and adds input message to error list
function errmsg(msg) {
    $('#error-field').show();
    var s = '<p class="err-add" style="color:red">';
    var v = s.concat(msg, '<br></p>');
    $(v).appendTo('#error-field');
}

//Checks mode, 1 is mcmc, 0 is load-genealogy
function mcmc() {
    return $('input[name="run-mode"]:checked').val() === 'm';
}


//Checks if variable is an integer, can probably be done better
function intCheck(n) {
    return n % 1 === 0;
}

//Adds red color to selected elements if the associated input is invalid
function addDanger(b1, b2, c) {
    $(b1).addClass('btn-danger');
    $(b2).addClass('btn-danger');
    $(c).addClass('bg-danger');
}

//Removes red color from selected elements
function removeDanger(b1, b2, c) {
    $(b1).removeClass('btn-danger');
    $(b2).removeClass('btn-danger');
    $(c).removeClass('bg-danger');
}

//Checks -b and -l options to see if they are present, and if so if they are integers or floats (controls run mode)
function blstat(s) {
    var v = $(s).val();
    if (v.length === 0) {
        return 0;
    }
    if (parseInt(v) === parseFloat(v)) {
        return 1;
    }
    return 2;
}

//Set what buttons on the job console are active
function setButtons(a,b,c,d,e) {
    $('#kill').attr('disabled','disabled');
    $('#delburn').attr('disabled','disabled');
    $('#delrun').attr('disabled','disbaled');
    $('#restart').attr('disabled','disabled');
    $('#removejob').attr('disabled','disabled');
    if(a === 1) { $('#kill').removeAttr('disabled'); }
    if(b === 1) { $('#delburn').removeAttr('disabled'); }
    if(c === 1) { $('#delrun').removeAttr('disabled'); }
    if(d === 1) { $('#restart').removeAttr('disabled'); }
    if(e === 1) { $('#removejob').removeAttr('disabled'); }
    return;
}

//Clears output area, sends server request for selected job's data
//Sets console buttons depending on job status
function changeJob() {
    document.getElementById('stdoutta').value = '';
    var id = $('#jobselect').val();
    ipcRenderer.send('change', {
        id: id
    });
}

ipcRenderer.on('change_response',function(e,data) {
    if (data.done === 0) {
        setButtons(1,data.burn,data.run,0,0);
    }
    else if(data.done === 1 || data.done === 2) {
        setButtons(0,0,0,1,1);
    }
    
});

//Code for testing, 'setvals' button is not currently in HTML
$('#demo-input').click(function () {
    $('#working-dir').val(pwd+sep+'sample'+sep);
    $('#infile').val('ima2_testinput.u');
    $('#outtag').val('testjob.out');
    $('#nametag').val('Test Job');
    $('#burn').val(1000);
    $('#run-time').val(1000);
    $('#t').collapse('toggle');
    $('#mps').val(3);
    $('#mpv').val(1);
    $('#mtps').val(2);
});

$('#analyze-link').click(function () {
    ipcRenderer.send('show-analysis');
});

$('#imfig-link').click(function () {
    ipcRenderer.send('show-imfig');
});

$('#help-link').click(function () {
    ipcRenderer.send('show-help');
});

//Probably redundant function
function getJobName() {
    var desc = $('#nametag').val();
    if( desc.length === 0) {
        desc = '';
    }
    return desc;
}

//Adds option to job menu, if sl != 0 then the job should be made active
function addJobOption(desc, id, sl) {
    var opt = '<option value="'.concat(id,'">',desc,'</option>');
    $(opt).appendTo('#jobselect');
    if(sl) {
        $('#jobselect').val(id);
        changeJob();
    }
}

//Determines burn/run modes, posts request with job info. Redundant prefix check is done on the server
//Assuming check passes, job is added to job menu and buttons are set appropriately
function submitJobRequest() {
    var s = printParams();
    //var o = $('#outtag').val();
    var o = getName('#outtag');
    var burn = 0;
    if(blstat('#burn') === 2 && document.getElementById('imburn-check').checked) {
        burn = 1;
    }
    var run = 0;
    if(blstat('#run-time') === 2 && document.getElementById('imrun-check').checked) {
        run = 1;
    }
    var name = getJobName();
    var num_process = $('#num-process').val().length !== 0 ? $('#num-process').val() : 1;
    ipcRenderer.send('run',{
        cmd: s,
        prefix: o,
        name: name,
        burn: burn,
        run: run,
        num_process: num_process
    });
    /*$.post('/', {
        post: 'run',
        cmd: s,
        prefix: o,
        name: name,
        burn: burn,
        run: run,
        num_process: num_process
    }, function (data) {
        if(data.fail === 1) {
            var msg = "Error: "+o+" is already stored as a used prefix, delete the job from the job manager to reuse";
            errmsg(msg);
        }
        else {
            $('#refresh').removeAttr('disabled');
            addJobOption(data.name,data.id,1);
            setButtons(1,burn,run,0,0);
        }
    });*/
}

ipcRenderer.on('run_response', function(e,data) {
    if(data.fail === 1) {
        var msg = "Error: "+data.prefix+" is already stored as a used prefix, delete the job from the job manager to reuse";
        errmsg(msg);
    }
    else {
        $('#refresh').removeAttr('disabled');
        addJobOption(data.name,data.id,1);
        setButtons(1,data.burn,data.run,0,0);
    }
});

//Sends request to validate all input filenames are present on user's file system.
//Submits job request if successful (normally done in calling function)
//An x value for a file indicates that file does not need to be checked for
function validatePaths() {
    var sendObj = {
        infile: '',
        paramf: 'x',
        titag: 'x',
        mcftag: 'x',
        nestedf: 'x'
    };
    var fl = 0;
    sendObj.infile = getName('#infile');
    if($('#c4').is(':checked')) { sendObj.paramf = getName('#paramf'); }
    if($('#r1').is(':checked')) { sendObj.titag = getName('#titag'); }
    if($('#r4').is(':checked')) { sendObj.mcftag = getName('#mcftag'); }
    if($('#c3').is('checked')) { sendObj.nestedf = getName('#nestedf'); }
    ipcRenderer.send('runvalidate',sendObj);
}

ipcRenderer.on('rv_response',function(e,data) {
    var fl = 0;
    if(data.infile === "1") {
        fl = 1;
        errmsg(sendObj.infile + ' is not a valid path for input file');
        $('#in-div').addClass('bg-danger');
    }
    if(data.paramf === "1") {
        fl = 1;
        errmsg(sendObj.paramf + ' is not a valid path for the parameter file');
        $('#c4-text').addClass('bg-danger');
        $('#b2').addClass('btn-danger');
    }
    if(data.titag === "1")  {
        fl = 1;
        errmsg(sendObj.titag + ' is not a valid path for the .ti file');
        $('#b5').addClass('btn-danger');
        $('#r1_text').addClass('bg-danger');
    }
    if(data.mcftag === "1") {
        fl = 1;
        errmsg(sendObj.mcftag + ' is not a valid path for the .mcf file');
        $('#b5').addClass('btn-danger');
        $('#r4_text').addClass('btn-danger');
    }
    if(data.nestedf === "1") {
        fl = 1;
        errmsg(sendObj.nestedf + ' is not a valid path for the nested model file');
        $('#b2').addClass('btn-danger');
        $('#c3_text').addClass('btn-danger');
    }
    if(fl === 0) {
        submitJobRequest();
    }
    
});

//Validates that all required fields are filled in and no incompatible options have been selected
//Returns 1 if options are valid, 0 if not
function validateArgs() {
    var fl = 0;
    var bf;
    var bs;
    //prior_check: mandatory prior fields not required in cmdline if prior file provided
    var prior_check = $('#c4').is(':checked') ? 0 : 1; 
    $('#error-field').hide();
    $('.err-add').remove();
    $('.btn-danger').removeClass('btn-danger');
    $('.bg-danger').removeClass('bg-danger');
    $('#valid').hide();
    if (v_check_line(document.getElementById('c3'), document.getElementById('nestedf').value) !== 1) {
        fl = 1;
        errmsg('Option "c2" requires filename for nested models');
        $('#c3_text').addClass('bg-danger');
        $('#b2').addClass('btn-danger');
    }
    if (v_check_line(document.getElementById('c4'), document.getElementById('paramf').value) !== 1) {
        fl = 1;
        alert('Option "c3" requires base name for parameter prior files');
        $('#c4_text').addClass('bg-danger');
        $('#b2').addClass('btn-danger');
    }
    if ((v_check_line(document.getElementById('p4'), document.getElementById('gen-time').value) !== 1) || (v_check_line(document.getElementById('p4'), document.getElementById('mut-rate').value) !== 1)) {
        fl = 1;
        errmsg('Option "p4" requires generation time and mutation rate');
        $('#p4_number').addClass('bg-danger');
        $('#b3').addClass('btn-danger');
    }
    if (v_check_line(document.getElementById('r1'), document.getElementById('titag').value) !== 1) {
        fl = 1;
        errmsg('Option "r0" requires base name for *ti files');
        $('#r1_text').addClass('bg-danger');
        $('#b5').addClass('btn-danger');
    }
    if (v_check_line(document.getElementById('r4'), document.getElementById('mcftag').value) !== 1) {
        fl = 1;
        errmsg('Option "r3" requires base name for *mcf files');
        $('#r4_text').addClass('bg-danger');
        $('#b5').addClass('btn-danger');
    }
    if ($('#j2').is(':checked') && $('#p6').is(':checked')) {
        fl = 1;
        errmsg('Incompatible options: j2 and p5');
        addDanger('#b3', '#b4', '.inc_j2_p6');
    }
    if ($('#j9').is(':checked') && $('#p6').is(':checked')) {
        fl = 1;
        errmsg('Incompatible options: j9 and p5');
        addDanger('#b3', '#b4', '.inc_j9_p6');
    }
    if ($('#j1').is(':checked') && $('#p5').is(':checked')) {
        fl = 1;
        errmsg('Incompatible options: j1 and p4');
        addDanger('#b3', '#b4', '.inc_j1_p5');
    }
    if ($('#infile').val().length === 0) {
        fl = 1;
        errmsg('Must provide input filename');
        $('#in-div').addClass('bg-danger');
    }
    if ($('#outtag').val().length === 0) {
        fl = 1;
        errmsg('Must provide output prefix');
        $('#out-div').addClass('bg-danger');
    }
    if (mcmc()) {
        if ($('#burn').val().length === 0) {
            fl = 1;
            errmsg('Must provide value for burn duration');
            $('#burn-div').addClass('bg-danger');
        }
        if ($('#run-time').val().length === 0) {
            fl = 1;
            errmsg('Must provide value for run duration');
            $('#run-div').addClass('bg-danger');
        }
        if (prior_check && $('#mps').val().length === 0) {
            fl = 1;
            errmsg('Must provide maximum population size');
            $('#b1').addClass('btn-danger');
            $('#mps-div').addClass('bg-danger');
        }
        if (prior_check && $('#mpv').val().length === 0) {
            fl = 1;
            errmsg('Must provide migration prior value');
            $('#b1').addClass('btn-danger');
            $('#mpv-div').addClass('bg-danger');
        }
        if (prior_check && $('#mtps').val().length === 0) {
            fl = 1;
            errmsg('Must provide value for maximum time of population split');
            $('#b1').addClass('btn-danger');
            $('#mtps-div').addClass('bg-danger');
        }
    }
    else {
        if($('#run-time') !== 1) {
            fl = 1;
            errmsg('Run duration must be provided');
            $('#run-div').addClass('bg-danger');
        }
    }
    if ($('#mc-check').is(':checked')) {
        if ($('#burn-noc').val().length === 0) {
            fl = 1;
            errmsg('Must prodive number of MC chains');
            alert($('#burn-noc').attr('min'));
            $('#bnoc-div').addClass('bg-danger');
            $('#b6').addClass('btn-danger');
        } else if (parseInt($('#burn-noc').val()) < parseInt($('#burn-noc').attr('min'))) {
            fl = 1;
            errmsg('MC number of chains must be greater or equal to '.concat($('#burn-noc').attr('min')));
            $('#bnoc-div').addClass('bg-danger');
            $('#b6').addClass('btn-danger');
        }
        bf = $('#burn-first').val();
        if (bf.length > 0 && (parseFloat(bf) < 0.9 || parseFloat(bf) > 1.1)) {
            fl = 1;
            errmsg('First burnin term must be between .9 and 1.1');
            $('#bfirst-div').addClass('bg-danger');
            $('#b6').addClass('btn-danger');
        }
        bs = $('#burn-second').val();
        if (bs.length > 0 && ( parseFloat(bs) <= 0.0 || parseFloat(bs) >= 1)) {
            fl = 1;
            errmsg('Second burnin term must be between 0 and 1');
            $('#bsecond-div').addClass('bg-danger');
            $('#b6').addClass('btn-danger');
        }
    }
    return 1-fl;
}

//Requests active jobs from server, done on page load. Adds active job options to job list
function getActiveLabels() {
    ipcRenderer.send('getlabels',{});
}

ipcRenderer.on('gl_response',function(e,data) {
    for (var i = 0; i < data.list.length; i++) {
        var fl = 0;
        if (i === data.list.length - 1) {
            fl = 1;
        }
        addJobOption(data.list[i].name, data.list[i].id,fl);
    }    
});

//When received from server, will add data to output window
//socket.on('process_data',function(data) {
ipcRenderer.on('process_data',function(e,data) {
    document.getElementById("stdoutta").value += data;
    var ta = document.getElementById("stdoutta");
    ta.scrollTop = ta.scrollHeight;
});

//Sets buttons after job finishes
//socket.on('end_job',function() {
ipcRenderer.on('end_job',function(e,data) {
    setButtons(0,0,0,1,1);
});

//socket.on('job_error', function(pth) {
ipcRenderer.on('job_error',function(e,pth) {
    setButtons(0,0,0,0,0);
    $('#stdoutta').val('The IMa2 executable was not found at path '+pth+', you can edit the IMA_PATH variable in index.js to the proper path');
});

//Sets buttons when signal is sent and accepted by job
//socket.on('burn-signal',function () {
ipcRenderer.on('burn-signal', function(e,data) {
    $('#delburn').attr('disabled','disabled');
});
//socket.on('run-signal', function () {
ipcRenderer.on('run-signal', function(e,data) {
    $('#delrun').attr('disabled','disabled');
});

$(document).ready(function () {
    //Adding until parallel windows version is distributed
    if(navigator.appVersion.indexOf("Win") != -1) {
        $('#num-process').attr('disabled','disabled');
    }
    $('#jobselect').change(function () {
        changeJob();
    });

    //Sends signal to kill active job
    $('#kill').click( function () {
        var id = $('#jobselect').val();
        ipcRenderer.send('kill', {id:id});
        setButtons(0,0,0,1,1);
    });


    //Sends signal to move on from current mode (burn or run)
    $('#delburn').click( function () {
        var id = $('#jobselect').val();
        ipcRenderer.send('delburn',{id:id});
    });
    
    $('#delrun').click( function () {
        var id = $('#jobselect').val();
        ipcRenderer.send('delrun',{id:id});
    });


    //Sets job status on server to 3 (done), removes job from client job list
    $('#removejob').click( function () {
        var id = $('#jobselect').val();
        ipcRenderer.send('remove',{id:id});
        setButtons(0,0,0,0,0);
        var js = '#jobselect option[value='.concat(id,']');
        $(js).remove();
        var length = $('#jobselect').children('option').length;
        if (length === 0) {
            document.getElementById('stdoutta').value = '';
            $('#refresh').attr('disabled','disabled');
        }
        else {
            changeJob();
        }
    });
    

//Restarts job with same parameters as originally passed
    $('#restart').click(function () {
        var id = $('#jobselect').val();
        document.getElementById('stdoutta').value = '';
        ipcRenderer.send('restart',{id:id});
    });
    
    ipcRenderer.on('restart_response',function(e,data) {
        setButtons(1,data.burn,data.run,0,0);
    });

//Refreshes output stream from server, shouldn't be necessary but just in case messages come in out of order
    $('#refresh').click(function () {
        var id = $('#jobselect').val();
        ipcRenderer.send('refresh',{id:id});
    });
    
    ipcRenderer.on('refresh_response',function(e,data) {
        document.getElementById('stdoutta').value = data.data;
    });

//Validates args, if valid will either send job request or check input file status (and send job request if files are valid)
    $('#bb').click(function () {
        console.log('click');
        var fl = validateArgs();
        if(fl === 0) { return 0; }
        var validate_paths = $('#validate-check').is(':checked');
        if(validate_paths) {
            validatePaths();
        }
        else {
            submitJobRequest();
        }

    });
    
    $('#bbbb').click(function () {
        ipcRenderer.send('test-signal','dataaaaaaaa');
    });

$('#j2').click(function () {
    "use strict";
    if (!($('#j2').is(':checked') && $('#p6').is(':checked'))) {
        $('.inc_j2_p6').removeClass('bg-danger');
    }
});

//Toggles heating term options and whether they should be included in command line
$("#mc-check").change(function () {
    "use strict";
    if ($(this).is(':checked')) {
        $('input.disableheat').attr("disabled", false);
    } else {
        $('input.disableheat').attr("disabled", true);
    }
});

//Enables/disables elements dependant on MCMC/Load-genealogy option
$('input[name="run-mode"]').click(function () {
    "use strict";
    var c = $('input[name="run-mode"]:checked').val();
    if (c === 'm') {
        $('.gl-el').attr("disabled", true);
        $('.mcmc-el').attr("disabled", false);
    } else {
        $('.gl-el').attr("disabled", false);
        $('.mcmc-el').attr("disabled", true);
    }
});

$("#c3").click(function () {
    "use strict";
    $("#c3_text").toggle();
});

//Sets minimum values for chain number, depending on linear or geometric mode
$('input[name="heating-type"]').click(function () {
    "use strict";
    var c = $('input[name="heating-type"]:checked').val();
    if (c === 'l') {
        $('#burn-noc').attr('min', 2);
    }
    if (c === 'g') {
        $('#burn-noc').attr('min', 4);
    }
});

//Toggles dropdown menus for option selection
$("#c4").click(function () {
    "use strict";
    $("#c4_text").toggle();
});

$("#p4").click(function () {
    "use strict";
    $("#p4_number").toggle();
});

$("#r1").click(function () {
    "use strict";
    $("#r1_text").toggle();
});

$("#r4").click(function () {
    "use strict";
    $("#r4_text").toggle();
});

$("#r6").click(function () {
    "use strict";
    $("#r6_int").toggle();
});

$('input').change(function () {
    "use strict";
    printParams();
});

});
