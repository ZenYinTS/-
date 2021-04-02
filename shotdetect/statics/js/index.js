$(function () {
    // 搜索内容的显示
    refreshContent()
    
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

//判断是否是图片
function isPic(url) {
    //- strFilter必须是小写列举
    var strFilter=".jpeg|.jpg|.png|"
    if(url.indexOf(".")>-1)
    {
        var p = url.lastIndexOf(".");
        var strPostfix=url.substring(p,url.length) + '|';
        strPostfix = strPostfix.toLowerCase();
        if(strFilter.indexOf(strPostfix)>-1)
            return true;

    }
    return false;
}