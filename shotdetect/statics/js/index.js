var myVideo = document.getElementById("myVideo")
var currentTime = $("#currentTime").val()

$(function () {
    // 搜索内容的显示
    refreshContent()

    //添加视频准备完成后的回调函数
    if (currentTime!=null){
        console.log("-------------  开始自动播放  -------------")
        myVideo.currentTime=parseFloat(currentTime); //跳转
        myVideo.play();            			//自动播放
    }


    //变量定义
    var urlInput = $("#urlInput")
    var divUpload = $("#divUpload")
    var btnUpload = $("#btnUpload")
    var btnSearch = $("#btnSearch")
    
    //本地上传按钮
    divUpload.click(function () {
        btnUpload.click()
    })

    //url输入框更新
    btnUpload.bind('change', function () {
        var fileName = $(this).val();
        var index = fileName.lastIndexOf("\\")
        fileName = fileName.substring(index+1,fileName.length)
        if(fileName.length>0){
            urlInput.val(fileName)
        }
    })

})

function refreshContent(){
    if ($("#urlInput").val().trim()==="") {
        $("#content").hide()
        return false
    }
    else {
        $("#content").show()
        return true
    }
}

$(".m-result").click(function () {
    var formdata = new FormData()
    // console.log($(this).data("result"))
    formdata.append('resVal',$(this).data("result"))
    formdata.append('csrfmiddlewaretoken', $('[name=csrfmiddlewaretoken]').val())

    $.ajax({
        url:"/search/show/",
        type:"post",
        data:formdata,
        processData: false, //加入这属性    processData默认为true，为true时，提交不会序列化data
        contentType: false,    // 不设置内容类型
        success:function (res) {
            // console.log(res)
            myVideo.setAttribute("src",res.src)
            //添加视频准备完成后的回调函数
            console.log("-------------  开始自动播放  -------------")
            myVideo.currentTime=res.frame_time;		    //跳转
            $("#currentTime").val(res.frame_time)
            myVideo.play();            			//自动播放

            $("#name").text(res.name)
            $("#similar").text(res.similar)
            $("#director").text(res.director)
            $("#starts").text(res.starts)
            $("#allNumber").text(res.allNumber)
            $("#number").text(res.number)
            $("#sTime").text(res.sTime)

        }


    })
})