/**
 * Created by jiemin on 9/22/17.
 */

var rangeDay = 30
var mealPerDay = 3
var chartOptions = {
    //Boolean - If we should show the scale at all
    showScale: true,
    //Boolean - Whether grid lines are shown across the chart
    scaleShowGridLines: false,
    //String - Colour of the grid lines
    scaleGridLineColor: 'rgba(0,0,0,.05)',
    //Number - Width of the grid lines
    scaleGridLineWidth: 1,
    //Boolean - Whether to show horizontal lines (except X axis)
    scaleShowHorizontalLines: true,
    //Boolean - Whether to show vertical lines (except Y axis)
    scaleShowVerticalLines: true,
    scaleOverride : true,
        scaleSteps : 10,
        scaleStepWidth : 10,
    //Boolean - Whether the line is curved between points
    bezierCurve: true,
    //Number - Tension of the bezier curve between points
    bezierCurveTension: 0.3,
    //Boolean - Whether to show a dot for each point
    pointDot: false,
    //Number - Radius of each point dot in pixels
    pointDotRadius: 4,
    //Number - Pixel width of point dot stroke
    pointDotStrokeWidth: 1,
    //Number - amount extra to add to the radius to cater for hit detection outside the drawn point
    pointHitDetectionRadius: 20,
    //Boolean - Whether to show a stroke for datasets
    datasetStroke: true,
    //Number - Pixel width of dataset stroke
    datasetStrokeWidth: 2,
    //Boolean - Whether to fill the dataset with a color
    datasetFill: true,
    //String - A legend template
    legendTemplate: '<ul class="<%=name.toLowerCase()%>-legend"><% for (var i=0; i<datasets.length; i++){%><li><span style="background-color:<%=datasets[i].lineColor%>"></span><%if(datasets[i].label){%><%=datasets[i].label%><%}%></li><%}%></ul>',
    //Boolean - whether to maintain the starting aspect ratio or not when responsive, if set to false, will take up entire container
    maintainAspectRatio: true,
    //Boolean - whether to make the chart responsive to window resizing
    responsive: true
}

var lineChartCanvas = $('#lineChart').get(0).getContext('2d')
var lineChart = new Chart(lineChartCanvas)
var lineChartOptions = chartOptions
lineChartOptions.datasetFill = true

//function freshLineChart(sql) {
//    $.post("/querydata", {sql: sql})
//        .done(function (data) {
//                  console.log(data)
//                  json_response = JSON.parse(data)
//                  //document.getElementById("output").innerHTML = JSON.stringify(json_response, null, 2);
//                  //console.log(json_response[1].image_id)
//                  //console.log(json_response[1].score)
//
//                  var xlabels = new Array(); // = ['9-16', 'February', 'March', 'April', 'May', 'June'];
//                  var ydata = new Array(); // = [28, 80, 400, 190, 860, 270];
//                  for (var i = 0; i < json_response.length; i++) {
//                      xlabels[i] = json_response[i].image_id;
//                      ydata[i] = json_response[i].score;
//                  }
//                  ;
//
//
//                  var chartData = {
//                      labels: xlabels,
//                      datasets: [
//                          {
//                              data: ydata,
//                              label: 'Digital Goods',
//                              fillColor: 'rgba(60,141,188,0.9)',
//                              strokeColor: 'rgba(60,141,188,0.8)',
//                              pointColor: '#3b8bba',
//                              pointStrokeColor: 'rgba(60,141,188,1)',
//                              pointHighlightFill: '#fff',
//                              pointHighlightStroke: 'rgba(60,141,188,1)'
//                          }
//                      ]
//                  }
//
//                  lineChart.Line(chartData, lineChartOptions)
//
//              })
//}

var imageScores
function getImageScores(count) {
    $.post("/queryscore", {count: count})
        .done(function (data) {
                  imageScores = JSON.parse(data)
                  console.log(imageScores)
                  drawLineChart(imageScores)
                  drawTotalScore(imageScores)
                  //drawMealPicture(imageScores)
                  drawMealPicture2(imageScores)
              })

}

//var imageLabels
//function getImageLabels() {
//    $.post("/querylabel", {count: count})
//        .done(function (data) {
//                  imageLabels = JSON.parse(data)
//              })
//}

function drawLineChart(imagescore) {
    var xlabels = new Array(); // = ['9-16', 'February', 'March', 'April', 'May', 'June'];
    var ydata = new Array(); // = [28, 80, 400, 190, 860, 270];
    for (var i = 0; i < imagescore.length && i < 30*mealPerDay; i++) {
        xlabels[i] = imagescore[i].input_time.substr(5,5)
        ydata[i] = imagescore[i].score
    }

    var chartData = {
        labels: xlabels.reverse(),
        datasets: [
            {
                data: ydata.reverse(),
                //label: 'Digital Goods',
                fillColor: 'rgba(60,141,188,0.9)',
                strokeColor: 'rgba(60,141,188,0.8)',
                pointColor: '#3b8bba',
                pointStrokeColor: 'rgba(60,141,188,1)',
                pointHighlightFill: '#fff',
                pointHighlightStroke: 'rgba(60,141,188,1)'
            }
        ]
    }

    lineChart.Line(chartData, lineChartOptions)
}

function drawTotalScore(imagescore) {
    var day7 = 0
    var day30 = 0
    var day7Length = 0
    var day30Length = 0
    for (var i = 0; i < imagescore.length && i < 7*mealPerDay; i++) {
        day7 += parseFloat(imagescore[i].score)
        day7Length = i
    }
    for (var i = 0; i < imagescore.length && i < 30*mealPerDay; i++) {
        day30 += parseFloat(imagescore[i].score)
        day30Length = i
    }
    $('#day7').html('Score: ' + parseInt(day7 / day7Length))
    $('#day30').html('Score: ' + parseInt(day30 / day30Length))
    $('#day7bar').css("width", parseInt(day7 / day7Length) + "%")
    $('#day30bar').css("width", parseInt(day30 / day30Length) + "%")
    $('#day7bg').addClass(parseInt(day7 / day7Length) > 59 ? "bg-green" : "bg-red")
    $('#day30bg').addClass(parseInt(day30 / day30Length) > 59 ? "bg-green" : "bg-red")
    $('#day7desc').html(parseInt(day7 / day7Length) > 59 ? "Healthy" : "Unhealthy")
    $('#day30desc').html(parseInt(day30 / day30Length) > 59 ? "Healthy" : "Unhealthy")
}

//function drawMealPicture(imagescore) {
//    for (var i = 0; i < imagescore.length && i < 5; i++) {
//        var imageid = imagescore[i].image_id
//        var pic_time = imagescore[i].input_time
//        var pic_src = "https://s3.amazonaws.com/" + imagescore[i].bucket + "/" + imagescore[i].image_name
//        var pic_score = imagescore[i].score
//        var pic_labels = new Array()
//        $.post("/querylabel", {imageid: imageid})
//            .done(function (data) {
//                      labels = JSON.parse(data)
//                      for (var i = 0; i < labels.length; i++) {
//                          pic_labels[i] = labels[i].label
//                      }
//                      var image_label_id = imageid
//                      document.getElementById("{0}".format(image_label_id)).innerHTML = pic_labels
//                      console.log('#' + imageid, pic_labels)
//                  })
//        addTimeItem(pic_time, pic_src, pic_score, imageid)
//        console.log(pic_time, pic_src, pic_score, imageid)
//    }
//
//}

function drawMealPicture2(imagescore) {
    var imageidlist = new Array()
    var pic_time = new Array()
    var pic_src = new Array()
    var pic_score = new Array()
    for (var i = 0; i < imagescore.length && i < 30*mealPerDay; i++) {
        imageidlist[i] = imagescore[i].image_id
        pic_time[i] = imagescore[i].input_time
        pic_src[i] = "https://s3.amazonaws.com/" + imagescore[i].bucket + "/" + imagescore[i].image_name
        pic_score[i] = imagescore[i].score
    }

    $.post("/querylabel2", {imageidlist: imageidlist.join()})
        .done(function (data) {
                  imagelabellistjson = JSON.parse(data)
                  console.log(imagelabellistjson)

                  for (var i = 0; i < imageidlist.length; i++) {
                      var pic_labels = new Array()
                      for (var j = 0; j < imagelabellistjson.length; j++) {
                          if (imagelabellistjson[j].image_id == imageidlist[i] && pic_labels.length < 5) {
                              pic_labels.push(imagelabellistjson[j].label)
                          }
                      }
                      addTimeItem2(pic_time[i], pic_src[i], pic_score[i], pic_labels)
                  }

              })
}

String.prototype.format = function () {
    var formatted = this;
    for (var arg in arguments) {
        formatted = formatted.replace("{" + arg + "}", arguments[arg]);
    }
    return formatted;
};

//function addTimeItem(pic_time, pic_src, pic_score, pic_id) {
//
//    var call_out = pic_score > 60 ? "callout-success" : "callout-danger"
//    var html_content = '<li><i class="fa fa-camera bg-purple"></i><div class="timeline-item"><h3 class="timeline-header">{0}</h3>'.format(pic_time) +
//        '<div class="timeline-body"><img src="{0}" alt="..." class="margin" style="height:150px">'.format(pic_src) +
//        ' <div class="callout {0}"><h4>Score: {1}</h4><p id="{2}"></p></div></div></div></li>'.format(call_out, pic_score, pic_id)
//    console.log(html_content)
//    $('#timelinelist').append(html_content)
//}

function addTimeItem2(pic_time, pic_src, pic_score, pic_labels) {

    var call_out = pic_score > 59 ? "callout-success" : "callout-warning"
    var html_content = '<li><i class="fa fa-camera bg-gray"></i><div class="timeline-item bg-gray"><h3 class="timeline-header">{0}</h3>'.format(pic_time) +
        '<div class="timeline-body"><img src="{0}" alt="..." class="margin" style="width:40%">'.format(pic_src) +
        ' <div class="callout {0}"><h4>Score: {1}</h4><p>Labels: {2}</p></div></div></div></li>'.format(call_out, pic_score, pic_labels)
    //console.log(html_content)
    $('#timelinelist').append(html_content)
}


function getUrlParam(name) {
 var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)"); //构造一个含有目标参数的正则表达式对象
 var r = window.location.search.substr(1).match(reg); //匹配目标参数
 if (r != null) return unescape(r[2]); return null; //返回参数值
}

window.onload = function () {
    //freshLineChart("select id as image_id, CAST(score AS CHAR ) as score, CAST(input_time AS CHAR)input_time from images limit 10")


    rangeDay = getUrlParam('rangeday') == null ? 30:getUrlParam('rangeday')
    mealPerDay = getUrlParam('mealperday') == null ? 3:getUrlParam('mealperday')

    getImageScores(rangeDay*mealPerDay)
    //addTimeItem("2017-09-22 03:12:50","https://s3.amazonaws.com/team2_image_in/food1.jpg","50","Fries, Chicken")

}