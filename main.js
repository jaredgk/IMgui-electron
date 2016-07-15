const electron = require('electron')
var jQuery = require('jquery')
var windowManager = require('electron-window-manager');
var exec = require('child_process').exec;
var spawn = require('child_process').spawn;
var os = require('os');
var fs = require('fs');
var path = require('path');
var require = electron.require;
var ipcMain = electron.ipcMain;
// Module to control application life.
const app = electron.app
// Module to create native browser window.
const BrowserWindow = electron.BrowserWindow

var dirPath = path.resolve(path.join(__dirname));
// Keep a global reference of the window object, if you don't, the window will
// be closed automatically when the JavaScript object is garbage collected.
let mainWindow

let analysisWindow;

let imfigWindow;

let helpWindow;

var debug = 1;
var winheight = 768;
var winwidth = 1024;

function createWindow () {
  // Create the browser window.
    global.sharedObj = { 
      pwd: __dirname,
      homedir: process.env[(os.platform() === 'win32') ? 'USERPROFILE' : 'HOME'],
      sep: ((os.platform() === 'win32') ? '\\' : '/')
  };
  mainWindow = new BrowserWindow({
      width: winwidth, 
      height: winheight
      })

  // and load the index.html of the app.
  mainWindow.loadURL(`file:${__dirname}/index.html`)

  // Open the DevTools.
  if(debug === 1) 
    mainWindow.webContents.openDevTools();

  // Emitted when the window is closed.
  mainWindow.on('closed', function () {
    // Dereference the window object, usually you would store windows
    // in an array if your app supports multi windows, this is the time
    // when you should delete the corresponding element.
    mainWindow = null
    analysisWindow = null;
    imfigWindow = null;
    helpWindow = null;
  })
    
}

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.on('ready', createWindow)

// Quit when all windows are closed.
app.on('window-all-closed', function () {
  // On OS X it is common for applications and their menu bar
  // to stay active until the user quits explicitly with Cmd + Q
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('activate', function () {
  // On OS X it's common to re-create a window in the app when the
  // dock icon is clicked and there are no other windows open.
  if (mainWindow === null) {
    createWindow()
  }
})

ipcMain.on('show-analysis', function () {
    analysisWindow = new BrowserWindow({
      width: winwidth,
      height: winheight
  });
  analysisWindow.loadURL('file://'+__dirname+'/analysis.html');
   /* analysisWindow.on('close',function(e) {
    e.preventDefault();
    analysisWindow.hide();
  });*/
    analysisWindow.show();
    if(debug === 1) 
        analysisWindow.webContents.openDevTools();
});

ipcMain.on('show-imfig', function () {
    imfigWindow = new BrowserWindow({
      width: winwidth,
      height: winheight
  });
  imfigWindow.loadURL('file://'+__dirname+'/imfig.html');
    imfigWindow.show();
    if(debug === 1) 
        imfigWindow.webContents.openDevTools();
});

ipcMain.on('show-help', function () {
    helpWindow = new BrowserWindow({
      width: winwidth,
      height: winheight
  });
  helpWindow.loadURL('file://'+__dirname+'/help.html');
    helpWindow.show();
    if(debug === 1) 
        helpWindow.webContents.openDevTools();
});



//Variables for job list and active index, paths to scripts and exes
var jobIdx = 0;
var jobList = [];
var IMA_PATH_UNIX = path.join(dirPath,'IMa','IMa2');
var IMA_PATH_WIN = path.join(dirPath,'IMa','IMa2.exe');
var IMFIG_PATH_UNIX = path.join(dirPath,'scripts','IMfig3');
var IMFIG_PATH_MAC = path.join(dirPath,'scripts','IMfig3-mac');
var IMFIG_PATH_WIN = path.join(dirPath,'scripts','IMfig3.exe');
var PATHTEST_PATH_UNIX = path.join(dirPath,'scripts','testpath.sh');
var PATHTEST_PATH_WIN = path.join(dirPath,'scripts','testpath.bat');
var PORT_NUMBER = 3000;
var DEBUG_FLAG = 0;

//Prints debug message if DEBUG_FLAG is less than priority.
//If DEBUG_FLAG = 0, all messages will be printed
function cLog(msg,priority) {
    if(priority >= DEBUG_FLAG) {
        console.log(msg);
    }
}
//Checks that no active job (state 0, 1, or 2) has the same prefix as the 
//submitted job. Return 0 if there's a duplicate, 1 if not
function checkUniqPrefix(pref) {
    for(var i = 0; i < jobList.length; i++) {
        if (jobList[i].status !== 3 && pref === jobList[i].prefix) { return 0; }
    }
    return 1;
}

//Returns the name of the job. If no name provided (length == 0), provide a default name (Job #(jobIdx)).
//If the job name is a duplicate, add job ID after for a unique name.
function getName(jobname) {
    if(jobname.length === 0) {
        return 'Job #'.concat(jobList.length + 1);
    }
    for(var i = 0; i < jobList.length; i++) {
        if(jobList[i].status !== 3 && jobname === jobList[i].name) {
            return jobname.concat(' (',jobList.length+1,')');
        }
    }
    return jobname;
}

function parseArgs(arg_string,num_process) {
    var arg_list = arg_string.trim().split(' ');
    var spawn_args = [];
    var cmd_args = [];
    if(os.platform() === 'win32') {
        spawn_args.push('cmd.exe');
        cmd_args.push('/C');
        cmd_args.push(IMA_PATH_WIN);
    } else if(os.platform() === 'linux' || os.platform() === 'darwin') {
        if(num_process == 1) {
            spawn_args.push(IMA_PATH_UNIX);
            console.log('single thread');
        } else {
            spawn_args.push('mpirun');
            cmd_args.push('-np',num_process,IMA_PATH_UNIX);
        }
    }
    for(var i = 0; i < arg_list.length; i++) {
        cmd_args.push(arg_list[i]);
    }
    spawn_args.push(cmd_args);
    return spawn_args;
}

/*Returns args for IMfig run. First arg is path to exe dependent on
  OS, followed by args from browser. Output arg is modified on windows
  systems to ensure path has correct separator

*/
function parseFigArgs(args) {
    var spawn_args = [];
    if(os.platform() === 'linux') { spawn_args.push(IMFIG_PATH_UNIX); }
    else if(os.platform() === 'win32') { spawn_args.push(IMFIG_PATH_WIN); }
    else if(os.platform() === 'darwin') { spawn_args.push(IMFIG_PATH_MAC); }
    var cmd_args = [];
    cLog(args,1);
    for(var i = 0; i < args.length; i++) {
        var t = args[i];
        if(args[i].substr(0,2) === '-o' && os.platform() === 'win32') {
            t = args[i].replace('/','\\');
        }
        cmd_args.push(t);
    }
    spawn_args.push(cmd_args);
    return spawn_args;
}


/*Takes req object and creates spawn args based on system to validate file
  paths. Replaces directory separators on windows. 
*/
function getValidateArgs(args) {
    var o = [];
    var l = [];
    if(os.platform() === 'win32') {
        o.push(PATHTEST_PATH_WIN);
    } else {
        o.push('sh');
        l.push(PATHTEST_PATH_UNIX);
    }
    for(var i = 0; i < args.length; i++) {
        var t = args[i];
        if(t.substring(0,2) === '-o' && os.platform() === 'win32') {
            var tt = t.replace('/','\\\\');
            t = tt;
        }
        l.push(t);
    }
    o.push(l);
    return o;
}

//Creates a job object from a request object body (req.body). 
function createJob(reqObj) {
    var tJob = {};
    tJob.name = getName(reqObj.name);
    tJob.id = jobList.length;
    tJob.prefix = reqObj.prefix;
    tJob.burn = reqObj.burn;
    tJob.run = reqObj.run;
    console.log(tJob.burn + ' ' + tJob.run);
    tJob.pipeout = '';
    tJob.errs = '';
    tJob.args = parseArgs(reqObj.cmd,reqObj.num_process);
    console.log(tJob.args);
    tJob.status = 0;
    tJob.pid = -1;
    return tJob;
}

//Sets jobIdx, pid, and spawns process
function startJob(job) {
    var id = job.id;
    jobIdx = id;
    if(job.burn == 1) {
        fs.writeFileSync(job.prefix+'.IMburn','y');
    }
    if(job.run == 1) {
        fs.writeFileSync(job.prefix+'.IMrun','y');
    }
    var e = spawn(job.args[0],job.args[1]);
    job.pid = e.pid;
    job.proc = e;
    e.stdout.setEncoding('utf-8');
    //Store stdout in job object, send to browser if job is selected
    e.stdout.on('data',function(data) {
        job.pipeout += data;
        if(id == jobIdx) {
            mainWindow.webContents.send('process_data',data);
        }
    });
    e.stderr.setEncoding('utf-8');
    //Handles signals for beginning/end of user-controlled burn/run modes
    e.stderr.on('data',function(data) {
        console.log(data);
        job.pipeout += data;
        if(id == jobIdx) {
            mainWindow.webContents.send('process_data',data);
        }
    });
    //Sends signal to browser to disable/enable appropriate buttons
    e.on("close",function(code) {
        console.log('close '+code);
        var s = 'close '+code+', run complete';
        job.pipeout += s;
        if(id == jobIdx) {
            mainWindow.webContents.send('process_data',s);
            if(code == -1) {
                var IMA_PATH;
                if(os.platform() === 'win32') { IMA_PATH = IMA_PATH_WIN; }
                else { IMA_PATH = IMA_PATH_UNIX; }
                mainWindow.webContents.send('job_error',IMA_PATH);
            } else {
                mainWindow.webContents.send('end_job');
            }
        }
        job.status = 2;
    });
    e.on("stop",function(code) {
        console.log('stop '+code);
        var s = 'stop '+code;
        job.pipeout += s;
        if(id == jobIdx) {
            mainWindow.webContents.send('process_data',s);
        }
        job.status = 1;
    });
    e.on("error",function(err) {
        console.log('error '+err);
        if (id == jobIdx) {
            mainWindow.webContents.send('process_data',err);
        }
        job.status = 1;
    });
}

ipcMain.on('run',function(e,data) {
    if(checkUniqPrefix(data.prefix) === 0) {
        var j = {
            fail: 1,
            prefix: data.prefix
        }
        e.sender.send('run_response',j);
    } else {
        var job = createJob(data);
        var j = { 
            id: job.id,
            name: job.name,
            fail: 0,
            burn: data.burn,
            run: data.run
        };
        e.sender.send('run_response',j);
        jobList.push(job);
        jobIdx = job.id;
        startJob(job);
    }    
    
    
});

ipcMain.on('runvalidate',function(e,data) {
    var nonexistlist = []
    var inname = data.infile;
    var paramf = data.paramf;
    var titag = data.titag;
    var mcftag = data.mcftag;
    var nestedf = data.nestedf;
    var arg_files = [inname,paramf,titag,mcftag,nestedf];
    var spawn_args = getValidateArgs(arg_files);
    var myProc = spawn(spawn_args[0],spawn_args[1], {
        shell: true
    });
    myProc.stdout.setEncoding('utf-8');
    myProc.stdout.on('data',function(data) {
        nonexistlist = data.replace('\n','').split(' ');
    });
    myProc.on('close', function(data) {
        console.log(nonexistlist);
        sendMsg = {
            infile: nonexistlist[0],
            paramf: nonexistlist[1],
            titag: nonexistlist[2],
            mcftag: nonexistlist[3],
            nestedf: nonexistlist[4]
        }
        e.sender.send('rv_response',sendMsg);
    });
});

ipcMain.on('change',function(e,data) {
    if (jobList.length === 0) {
        var j = {
            done: -1,
            stat: 'none'
        }
    } else {
        var id = data.id;
        jobIdx = id;
        console.log(jobIdx);
        mainWindow.webContents.send('process_data',jobList[jobIdx].pipeout);
        var j = {
            done: jobList[id].status,
            burn: (jobList[id].burn == 1) ? 1 : 0,
            run: (jobList[id].run == 1) ? 1 : 0
        };
    }
    e.sender.send('change_response',j);
    
});

ipcMain.on('getlabels', function(e,data) {
    j = {
        list: []
    };
    for(var i = 0; i < jobList.length; i++) {
        if (jobList[i].status !== 3) {
            var t = { name: jobList[i].name, id: jobList[i].id };
            j.list.push(t);
        }
    }
    e.sender.send('gl_response',j);
});

ipcMain.on('kill',function(e,data) {
    var id = data.id;
    /*var cmd = 'kill -9 '.concat(jobList[id].pid);
    var e = exec(cmd);*/
    if(os.platform() === 'win32') {
        spawn("taskkill", ['/pid',jobList[id].pid,'/f','/t']);
    } else {
        jobList[id].proc.kill('SIGINT');
    }
    jobList[id].pid = -1;
    jobList[id].status = 1; 
});

ipcMain.on('remove',function(e,data) {
    var id = data.id;
    if(jobList[id].status !== 0) {
        jobList[id].status = 3;
    } else {
        console.log('Warning: job removal of job with status 0');
    }
});

ipcMain.on('restart',function(e,data) {
    var id = data.id;
    var job = jobList[id];
    job.pipeout = '';
    job.errs = '';
    job.status = 0;
    startJob(jobList[id]);
    sendf = 1;
    if(job.burn == 2) { job.burn = 1; }
    if(job.run == 2) { job.run = 1; }
    var j = {
        burn: (jobList[id].burn == 1) ? 1 : 0,
        run: (jobList[id].run == 1) ? 1 : 0
    }
    e.sender.send('restart_response',j);
});

ipcMain.on('imfig', function(e,data) {
    var s_args = parseFigArgs(data.args); //This might be weird
    var pref = data.prefix;
    pref += '.eps';
    var fullpath = path.join(__dirname,pref);
    console.log(s_args);
    var s = spawn(s_args[0],s_args[1]);
    var response_sent = 0;
    var errfl = 0;
    var errlog = '';
    s.stdout.on('data', function(data) {
        console.log(data);
    });
    s.stderr.on('data', function(data) {
        console.log('error: '+data);
        errlog += data;
        //imfigWindow.webContents.send('imfig_response',{fail: 1, msg: data});
        errfl = 1;
    });
    s.on('close',function () {
        if(response_sent === 0 && errfl === 0) {
            var j = {
                fail: 0,
                path: fullpath,
                prefix: data.prefix
            };
            response_sent = 1;
            e.sender.send('imfig_response',j);
        }
        if(response_sent === 0 && errfl === 1) {
            var j = {
                fail: 1,
                msg: errlog
            };
            e.sender.send('imfig_response',j);    
        }
    });
    s.on('error',function (err) {
        errlog += err;
        console.log(JSON.stringify(err));
        var j = {
            fail: 1,
            msg: errlog
        };
        if(response_sent === 0) {
            response_sent = 1;
            e.sender.send('imfig_response',j);
        }
    });    
    
});

ipcMain.on('delburn',function(e,data) {
    var id = data.id;
    var job = jobList[id];
    fs.unlink(job.prefix+'.IMburn', function (err) {
        if(!err) {
            job.burn = 2;
            mainWindow.webContents.send('burn-signal');
                
        }
    });
});

ipcMain.on('delrun',function(e,data) {
    var id = req.body.id;
        var job = jobList[id];
        fs.unlink(job.prefix+'.IMrun', function (err) {
            if(!err) {
                job.run = 2;
                mainWindow.webContents.send('run-signal');
            }
        });
});

ipcMain.on('refresh', function(e,data) {
    var id = data.id;
    var j = {
        data: jobList[id].pipeout
    }
    mainWindow.webContents.send('refresh_response',j);
});

// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and require them here.
ipcMain.on('test-signal', function () {
    console.log('signal sent');
    var p = path.join(dirPath,'IMa2');
    var proc = spawn(p,['-h']);
    proc.stdout.setEncoding('utf-8');
    proc.on('close', function (e) {
        console.log('random number generated');
        console.log(e);
        mainWindow.webContents.send('test_response','hello from the other side');
    });
    proc.on('error', function (e) {
        console.log('error');
        console.log(e);
    });
    proc.stdout.on('data',function(data) {
        console.log(data);
    });
});
