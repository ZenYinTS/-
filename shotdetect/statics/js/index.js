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

    //搜索按钮事件
    // btnSearch.click(function () {
    //     var url = urlInput.val().trim()
    //     if (url === "") {
    //         $(".ui.mini.modal>.header").text("url不可为空！")
    //         $(".ui.mini.modal").modal('show')
    //     }
    //     else {
    //         if (isPic(url)){
    //             //从数据库查找三种可能结果，更新面板
    //
    //             //显示查询结果
    //             $("#content").show()
    //         }else {
    //             $(".ui.mini.modal>.header").text("url非法！请输入图片url！")
    //             $(".ui.mini.modal").modal('show')
    //             $("#content").hide()
    //         }
    //     }
    //
    // })

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