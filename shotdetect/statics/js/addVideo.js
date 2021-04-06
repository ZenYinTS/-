$("#fileInput").click(function () {
    $("#btnFileInput").click()
})

$("#btnFileInput").bind('change', function () {
    var fileName = $(this).val();
    var index = fileName.lastIndexOf("\\")
    fileName = fileName.substring(index + 1, fileName.length)
    if (fileName.length > 0) {
        $("#fileInput").val(fileName)
    }
    // 上传视频
    //创建对象
    var formdata = new FormData();
    //这里FormData是一个jquery对象，用来绑定values对象，也可以用来上传二进制文件，有了他就可以不用form表单来上传文件了

    var file_obj = $('#btnFileInput')[0].files[0];
    formdata.append('uploadID', $("[name='uploadID']").val());
    formdata.append('file_obj', file_obj);
    formdata.append('fileName', fileName);
    formdata.append('csrfmiddlewaretoken', $('[name=csrfmiddlewaretoken]').val())
    //设置窗口可见
    $("#msgUploading").show()

    $.ajax({
        url: "/videoManage/uploadVideo/",
        type: "post",
        data: formdata,
        processData: false,    // 不处理数据
        contentType: false,    // 不设置内容类型
        success: function (res) {
            // console.log(res)
            // console.log(res.file_time)
            // 上传成功
            var msg = "上传成功！";
            $("#msgUploadResult>.header").text(msg)
            $("#msgUploadResult").show()
            // 设置窗口不可见
            $("#msgUploading").hide()

            // 设置时长\路径\uploadID
            $("[name='vTime']").val(res.file_time)
            $("[name='path']").val(res.path)
            $("[name='uploadID']").val(res.uploadID)

            // 设置按钮可用
            $("#btnSubmit").attr('disabled', false)
            $("#btnReset").attr('disabled', false)

        },
        error:function (res) {
            console.log(res)
            // 上传失败
            var msg = "上传失败！";
            $("#msgUploadResult>.header").text(msg)

            $("#msgUploadResult").show()
            // 设置窗口不可见
            $("#msgUploading").hide()
        }

    })
})