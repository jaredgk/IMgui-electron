/*global alert, $, jQuery, FileReader*/

/*IMgui 2016- Jared Knoblauch, Arun Sethuraman, and Jody Hey*/

var xmlDoc; //XML file contents
var xmlFile; //"histogram" or "main:
var xmlArray = []; //Stores parsed file contents, indexes correspond to menu option number

//require('d3');

//Creates tick mark array, then calls c3 library to make chart
function createChart(a,b) {
    //Create 11 tick marks for x-axis
    var ticks = []
    for (i = 0; i <= 10; i++) {
        var cv = ((i)/10*a[a.length-1]+((10-i)/10)*a[1]).toFixed(2);
        ticks.push(cv);
    }
    console.log(a[0]);
    var chart = c3.generate({
        data: {
            x: 'x',
            columns: [
                a,
                b
            ]
        },
        interaction: {
            enabled: false
        },
        axis: {
            x: {
                tick: {
                    values: ticks
                }
            }, 
            y: {
                label: {
                    text: 'Posterior Probability',
                    position: 'outer-middle'
                }
            }
        },
        point: {
            show: false
        }
    });
}

//Given a list of variables, will populate the graphing dropdown menu
function createPullTab(s) {
    $('#colid').empty().show();
    var va = $.trim(s).split(/[ ][ ]*/);
    for(i = 0; i < va.length; i++) {
        var opt = '<option value="'.concat(i,'">',va[i],'</option>');
        $(opt).appendTo('#colid');
    }
}

//Parses XML to create object with description, parameters (variables), and data
//Data in XML format
function makeHistogramObject(x) {
    var obj = {};
    obj.description = x.getAttribute('description');
    for(i = 0; i < x.childNodes.length; i++) {
        if(x.childNodes[i].nodeName === "Parameter") {
            obj.parameters = x.childNodes[i].childNodes[0].nodeValue;
        }
        if(x.childNodes[i].nodeName === "Data") {
            obj.data = x.childNodes[i].childNodes;
        }
    }
    return obj;
}

//Parses loaded XML data to create histogram objects for every histogram in the input file
//Creates pull tab
function loadHistogram() {
    var x = xmlDoc.documentElement.childNodes;
    $('#svgdiv').show();
    $('#tablediv').hide();
    $('#savefiletable').hide();
    $('#chartdiv').show();
    var i, j = 0;
    for(i = 0; i < x.length; i++) {
        if(x[i].nodeName === "Histogram") {
            var obj = makeHistogramObject(x[i]);
            xmlArray.push(obj);
            var opt = '<option value="'.concat(j,'">',obj.description,'</option>');
            $(opt).appendTo('#selectid');
            j += 1
        }
    }
    createPullTab(xmlArray[0].parameters);
}

//Creates header, with a subheader if that information is provided
function createHeader(xmlobj) {
    var heada = $.trim(xmlobj.head).split(/[ ][ ]*/);
    var thr = '';
    if (xmlobj.sub.length != 0) {
        var suba = $.trim(xmlobj.sub).split(/[ ][ ]*/);
        var span = suba.length;
        thr += '<tr><th></th>';
        for(var i = 0; i < heada.length; i++) {
            thr += '<th colspan='.concat(span,'>',heada[i],'</th>');
        }
        thr += '<tr><th></th>';
        for(var i = 0; i < heada.length; i++) {
            for(var j = 0; j < suba.length; j++) {
                var el = '<th>'+suba[j]+'</th>';
                thr += el;
            }
        }
        thr += '</tr>';
    }
    else {
        thr += '<tr>';
        for(var i = 0; i < heada.length; i++) {
            var el = '<th>'+heada[i]+'</th>';
            thr += el;
        }
        thr += "</tr>";
    }
    $('#outtable').append(thr);
}

//Given a loaded XML object, will create HTML table from the given node in the XML file
//Data in XML node have alternating element/text nodes, so for loop increments by 2
function createTable(xmlobj) {
    $('#outtable').empty();
    var data = xmlobj.data;
    var i;
    var trr = '';
    createHeader(xmlobj);
    for(i = 1; i < data.length; i+=2) {
        //trr += '<tr><td>'.concat(data[i].getAttribute('row'),'</td>');
        trr += '<tr>';
        la = $.trim(data[i].childNodes[0].nodeValue).split(/[ ][ ]*/);
        for(ii = 0; ii < la.length; ii++) {
            var tdd = '<td>'.concat(la[ii],'</td>');
            trr+=tdd;
        }
        trr += '</tr>';
    }
    $('#outtable').append(trr);
}

//Gets filename for table for .png save
function getPngName() {
    var name = $('#savefilevaltable').val();
    if (name.length == 0) { name = 'IMA_table'; }
    if (name.length - name.indexOf('.png') === 4) { return name; }
    name += '.png';
    return name;
}
        
//Parses tables, creating table objects with description, data, and headers
//Displays fist table afterwards
function loadMain(){
    var x = xmlDoc.documentElement.childNodes;
    var j = 0;
    $('#selectid').show();
    $('#tablediv').show();
    $('#svgdiv').hide();
    $('#savefilechart').hide();
    $('#savefiletable').show();
    $('#chartdiv').hide();
    for(i = 0; i < x.length; i++) {
        if(x[i].nodeName === "HighestPDG") {
            var obj = {}
            obj.description = x[i].childNodes[0].nodeValue;
            obj.data = x[i].childNodes[3].childNodes;
            obj.head = x[i].childNodes[1].childNodes[0].nodeValue;
            obj.sub = '';
            xmlArray.push(obj);
            var opt = '<option value="'.concat(j,'">',obj.description,'</option>');
            $(opt).appendTo('#selectid');
            j += 1;
        }
        else if(x[i].nodeName === "AcceptanceRates") {
            for(ii = 0; ii < x[i].childNodes.length; ii++) {
                if(x[i].childNodes[ii].nodeName === 'UpdateRates') {
                    var obj = {};
                    obj.description = x[i].childNodes[ii].childNodes[0].nodeValue;
                    obj.data = x[i].childNodes[ii].childNodes[5].childNodes;
                    obj.head = x[i].childNodes[ii].childNodes[1].childNodes[0].nodeValue;
                    obj.sub = x[i].childNodes[ii].childNodes[3].childNodes[0].nodeValue;
                    xmlArray.push(obj);
                    var opt = '<option value="'.concat(j,'">',obj.description,'</option>');
                    $(opt).appendTo('#selectid');
                    j += 1;
                }
            }
        }
        else if(x[i].nodeName === "SwapRates") {
            for(ii = 0; ii < x[i].childNodes.length; ii++) {
                if(x[i].childNodes[ii].nodeName === "SwapTable") {
                    var obj = {};
                    obj.description = x[i].childNodes[ii].childNodes[0].nodeValue;
                    obj.head = x[i].childNodes[ii].childNodes[1].childNodes[0].nodeValue;
                    obj.data = x[i].childNodes[ii].childNodes[3].childNodes;
                    obj.sub = '';
                    xmlArray.push(obj);
                    var opt = '<option value="'.concat(j,'">',obj.description,'</option>');
                    $(opt).appendTo('#selectid');
                    j += 1;
                }
            }
        }
        else if(x[i].nodeName === "CurrentVals") {
            for(ii = 0; ii < x[i].childNodes.length; ii++) {
                if(x[i].childNodes[ii].nodeName === "ValTable") {
                    var obj = {};
                    obj.description = x[i].childNodes[ii].childNodes[0].nodeValue;
                    obj.head = x[i].childNodes[ii].childNodes[1].childNodes[0].nodeValue;
                    obj.data = x[i].childNodes[ii].childNodes[3].childNodes;
                    obj.sub = '';
                    xmlArray.push(obj);
                    var opt = '<option value="'.concat(j,'">',obj.description,'</option>');
                    $(opt).appendTo('#selectid');
                    j += 1;
                }
            }
        }
        else if(x[i].nodeName === "MVC") {
            var obj = {}
            obj.description = x[i].childNodes[0].nodeValue;
            obj.data = x[i].childNodes[3].childNodes;
            obj.head = x[i].childNodes[1].childNodes[0].nodeValue;
            obj.sub = '';
            xmlArray.push(obj);
            var opt = '<option value="'.concat(j,'">',obj.description,'</option>');
            $(opt).appendTo('#selectid');
            j += 1;
        }
    }
    createTable(xmlArray[0]);
}



//Creates new table or histogram from loaded XML file
$('#selectid').change(function () {
    var ii = $('#selectid option:selected').val();
    if(xmlFile === "histograms") {
        createPullTab(xmlArray[ii].parameters);
    }
    if(xmlFile === "main" || xmlFile === "intervals") {
        createTable(xmlArray[ii]);
    }
});

//Pulls selected column from loaded XML file
//headrows: 0 means no column headers
function createCols(headrows) {
    var ii = $('#selectid option:selected').val();
    var jj = $('#colid option:selected').val();
    var varname = $('#colid option:selected').text();
    var a = [];
    var b = [];
    if(headrows !== 0) {
        a.push('x');
        b.push(varname);
    }
    var x = xmlArray[ii].data;
    for(var i = 1; i < 2001; i+=2) {
        var row = x[i].childNodes[0].nodeValue.split(/[ ][ ]*/);
        a.push(parseFloat(row[jj*2]));
        b.push(parseFloat(row[jj*2+1]));
    }
    return [a,b];
}

//Calls function to create chart from selected data
$('#makegraph').click(function () {
    $('#savefilechart').show();
    var o = createCols(1);
    a = o[0];
    b = o[1];
    createChart(a,b);
});

//Saves active histogram as image
$('#savebutton').click( function () {
    var name = $('#savefilevalchart').val();
    if (name.length == 0) { name = 'IMA_output'; }
    if(name.length - name.indexOf('.png') !== 4) { name += ".png"; }
    saveSvgAsPng(document.getElementById("chart"),name,{scale:2});
});

//Saves active table as image
$('#tablesavepng').click( function () {
    $('#outtable').tableExport({type:'png',escape:'false'});
});

//Creates .csv formatted table, then creates URI for download
function createCsvUri(a,b,varname) {
    var csv = varname + ',values\n';
    for(var i = 1; i < a.length; i++) {
        csv += (a[i].toString() + ',' + b[i].toString() + '\n');
    }
    var csvUri = 'data:application/csv;charset=utf-8,' + encodeURIComponent(csv);
    return csvUri;
}

//Gets name, assigns URI to download button
function csvDownload(csv) {
    var name = $('#savefilevalchart').val();
    if(name.length == 0) { name = 'IMA_columns'; }
    if(name.length - name.indexOf('.csv') !== 4) { name += '.csv'; }
    $(this).attr({
        'download': name,
        'href': csv,
        'target': '_blank'
    });
}

//Saves histogram columns to csv
$('#savecolstocsv').click( function () {
    var o = createCols(1);
    var a = o[0];
    var b = o[1];
    var varname = $('#colid option:selected').text();
    var csv = createCsvUri(a,b,varname);
    csvDownload.apply(this,[csv]);
});

//Can be used to hide code block
$('#codebutton').click( function () {
    $('#codediv').toggle();
});

//Splits large arrays based on max character line length. If max_length == 0, 
//returns a one-line string in specified language. Otherwise, creates a multi-
//line string
function splitArrayToLines(a,varname,max_length,language) {
    var s = '', line = '', delim = ',', line_delim = '\n';
    var pre_space, end_space, end_char;
    if(language === 0) {
        pre_space = 4;
        end_space = max_length - 1;
        line = (varname + ' = [');
        end_char = ']';
    } else if (language === 1) {
        pre_space = 7;
        end_space = max_length - 1;
        line = (varname + ' <- c(');
        end_char = ')';
    } else if (language === 2) {
        pre_space = 4;
        end_space = max_length - 4;
        line = (varname + ' = [');
        delim = ' ';
        end_char = '];';
        line_delim = '...\n';
    }
    if(max_length === 0) {
        return (line + a.toString() + end_char + '\n');
    }
    for(var i = 0; i < a.length; i++) {
        var t = a[i].toString();
        if (line.length + t.length > end_space) {
            line += line_delim;
            s += line;
            line = '';
            for(var ii = 0; ii < pre_space; ii++) { line += ' '; }
        }
        line += t;
        if(i !== (a.length - 1)) {
            line += delim;
        } else {
            console.log('end');
            line += (end_char+'\n');
            s += line;
        }
    }
    return s;
}


//Creates URI that is linked to download code button, pulls name from input field
function downloadCode() {
    var codedata = $('#codearea').val();
    var dldata = 'data:application/txt;charset=utf-8,'+encodeURIComponent(codedata);
    var name = $('#code-prefix').val();
    if(name.length === 0) {
        name = 'ima_code_plot';
    }
    var lang = $('#codeselect option:selected').val();
    if (lang == 0) { name += '.py'; }
    else if (lang == 1) { name += '.R'; }
    else if (lang == 2) { name += '.m'; }
    $(this).attr({
        'download': name,
        'href': dldata,
        'target': '_blank'
    });
}

//Generates simple matplotlib code and displays in text area
function generateCodeMPL(a,b,xl,max_length) {
    var h = "import matplotlib.pyplot as plt\n";
    h += "import numpy as np\n\n";
    h += splitArrayToLines(a,'x',max_length,0);
    h += splitArrayToLines(b,'y',max_length,0);
    h += "xl = '"+xl+"'\n";
    h += "plt.plot(x,y)\n\n";
    h += "plt.xlabel(xl)\n";
    h += "plt.ylabel('Estimated Posterior Probability')\n";
    h += "plt.title('IMa Plot')\n";
    h += "plt.grid(True)\n";
    h += "plt.show()\n";
    $('#codearea').val(h);
}

//Generates simple R code and displays in text area
function generateCodeR(a,b,xl,max_length) {
    var h = splitArrayToLines(a,'x',max_length,1);
    h += splitArrayToLines(b,'y',max_length,1);
    h += "plot(x,y,xlab='"+xl+"',ylab='Estimated Posterior Probability',main='IMa Plot')\n";
    $('#codearea').val(h);   
}

//Generates simple matlab code and displays in text area
function generateCodeMatlab(a,b,xl,max_length) {
    var h = "";
    h += splitArrayToLines(a,'x',max_length,2);
    h += splitArrayToLines(b,'y',max_length,2);
    h += "figure\n";
    h += "plot(x,y);\n";
    h += "title('IMa Plot')\n";
    h += "xlabel('"+xl+"')\n";
    h += "ylabel('Estimated Posterior Probability')\n";
    $('#codearea').val(h);
}

//Switch function for generating code
$('#codeproduce').click( function () {
    var o = createCols(0);
    var a = o[0];
    var b = o[1];
    var opt = $('#codeselect option:selected').val();
    var xl = $('#colid option:selected').text();
    var max_length = 0;
    if(document.getElementById('code_line_length').value) {
        max_length = document.getElementById('code_line_length').value;
    }
    if(opt === '0') {
        generateCodeMPL(a,b,xl,max_length);
    } else if (opt === '1') {
        generateCodeR(a,b,xl,max_length);
    } else if (opt === '2') {
        generateCodeMatlab(a,b,xl,max_length);
    }
    
});

//Runs download code function, pulling data from the output text box
$('#codedownload').click( function () {
    if($('#codearea').val() !== '') {
        downloadCode.apply(this)
    }
});

$(document).ready( function () {
//On click, will check for valid XML file/filename, then clear existing graph/table, populate select tab, identify file type, and call appropriate display function
$('#xmlsb').click(function () {
    var files = document.getElementById('xmlup').files;
    console.log(document.getElementById('xmlup').files[0].path);
    if(files.length === 0) {
        alert('Must provide an XML output file');
        return;
    }
    xmlArray = [];
    $('#selectid').empty();
    $('#colid').empty();
    $('#chart').empty();
    $('#select-div').show();
    var s;
    if(files.length === 1) {
        var f = files[0];
        var xmln = document.getElementById('xmlup').value;
        if(xmln.indexOf('.histograms.xml') > -1) {
            xmlFile = 'histograms';
        } else if(xmln.indexOf('.intervals.xml') > -1) {
            xmlFile = 'intervals';
        } else if(xmln.indexOf('.xml') > -1) {
            xmlFile = 'main';
        } else {
            alert('Error: Did not provide an XML file');
            return;
        }
        var reader = new FileReader();
        reader.onloadend = function (e) {
            if (e.target.readyState == FileReader.DONE) {
                s = e.target.result;
                xmlDoc = $.parseXML(s);
                if(xmlFile === "histograms"){
                    loadHistogram();
                }
                if(xmlFile === "main" || xmlFile === "intervals") {
                    loadMain();
                }
            }
        }
        reader.readAsText(f);
    }
});
    
});
    
