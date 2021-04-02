function page(btn) {
    //获取上一页下一页中自定义的page属性值，赋值给隐含域
    $("[name='page']").val($(btn).data("page"));
    loadData();
}

//搜索按钮的点击事件
$("#btnSearch").click(function () {
    $("[name='page']").val(0);
    loadData();
});

function loadData() {
    $("#table-container").load(/*[[@{/admin/blogs/search}]]*/"/admin/blogs/search", {
        title: $("[name='title']").val(),
        typeId: $("[name='typeId']").val(),
        recommend: $("[name='recommend']").prop('checked'),
        page: $("[name='page']").val()
    });
}

$('.message .close')
    .on('click', function () {
        $(this)
            .closest('.message')
            .transition('fade');
    });
$('#clear')
    .on('click', function () {
        $('.type.ui.dropdown')
            .dropdown('clear')
        ;
    })
;