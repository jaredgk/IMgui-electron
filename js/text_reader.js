/*global alert, $, jQuery, FileReader*/

var windowManager = require('electron').remote.require('electron-window-manager');
var ipcRenderer = require('electron').ipcRenderer;
var remote = require('electron').remote;

ipcRenderer.on('file-contents',function(e,pth,data) {
    console.log('getting contents');
    $(document).prop('title',pth);
    $('#text-area').val(data);
});

ipcRenderer.on('file-not-found', function(e,pth) {
    $('#text-area').val(pth+' is not a valid filepath on your system');
});

//ipcRenderer.send('read-file');
