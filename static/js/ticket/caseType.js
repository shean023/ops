// 获取用户名单,设置(工单处理人)下拉选择框
function getUsers() {
    $.ajax({
        url: '/users/get_user/',
        type: "POST",
        dataType: "json",
        data: {'oper': "getUsers"},
        error: function () {
            alert("拉取工单处理人 Error!");
        },
        success: function (data) {
            $("#casetype_executor").append('<option value="0">--选择工单处理人--</option>');

            for (key_num in data['data']) {
                $("#casetype_executor").append('<option value="' + data['data'][key_num]['id'] + '">' + data['data'][key_num]['cnname'] + '(' + data['data'][key_num]['name'] + ')</option>');
            }
            ;

        }
    });
}

// 添加(执行人)下拉选择框样式
function addExecutorCSS(obj) {
   if ($(obj).prev().is("select")) {
        var preval = $(obj).prev().val();
    } else if ($(obj).prev().is("span")) {
        var preval = $(obj).prev().find(".executor").val();
    }

    var hasboss = false;
    $(".executor").each(function () {
        if ($(this).val() == "-1") {
            hasboss = true;
        }
    })

    // if (preval == "-1") {
    //     hasboss = true;
    // }

    if (hasboss == true) {  //前面是默认上级,那么后面只能是指定人选了

        var len = $(".executor").length;
        $(obj).before('<span class="moreexecutor"><span class="glyphicon glyphicon-arrow-right"></span><select class="select2 executor" id="executor_' + len + '" onchange="changeExecutor(this);" style="width:140px" num="0"><option value = "-2">指定人选</option></select></span>');
        getCheckLeader($("#executor_" + len), 'execute');
    } else {
        $(obj).before('<span class="moreexecutor"><span class="glyphicon glyphicon-arrow-right"></span><select class="select2 executor" onchange="changeExecutor(this);" style="width: 140px"> <option value="-1">默认上级</option><option value = "-2">指定人选</option></select></span>')
    }


    if ($(obj).next().is("a")) {
    } else {
        $(obj).after('<a class="btn btn-xs btn-primary" onclick="delCheckLeaderCSS(this)" style="margin-left: 5px" id="delexecutor">删除一级</a>')
    }
}

// 添加(审核人)下拉选择框样式
function addCheckLeaderCSS(obj) {
    if ($(obj).prev().is("select")) {
        var preval = $(obj).prev().val();
    } else if ($(obj).prev().is("span")) {
        var preval = $(obj).prev().find(".checkleader").val();
    }

    var hasboss = false;
    $(".checkleader").each(function () {
        if ($(this).val() == "-1") {
            hasboss = true;
        }
    })
    // if (preval == "-1") {
    //     hasboss = true;
    // }
    if (hasboss == true) {  //前面是默认上级,那么后面只能是指定人选了
        var len = $(".checkleader").length;
        $(obj).before('<span class="morecheckleader"><span class="glyphicon glyphicon-arrow-right"></span><select class="select2 checkleader" id="checkleader_' + len + '" onchange="changeCheckLeader(this);" style="width:140px" num="0"><option value = "-2">指定人选</option></select></span>');
        getCheckLeader($("#checkleader_" + len),'check');
    } else {
        $(obj).before('<span class="morecheckleader"><span class="glyphicon glyphicon-arrow-right"></span><select class="select2 checkleader" onchange="changeCheckLeader(this);" style="width: 140px"> <option value="-1">默认上级</option><option value = "-2">指定人选</option></select></span>')
    }
    if ($(obj).next().is("a")) {
    } else {
        $(obj).after('<a class="btn btn-xs btn-primary" onclick="delCheckLeaderCSS(this)" style="margin-left: 5px" id="delcheckleader">删除一级</a>')
    }
}

// 删除(审核人,执行人)下拉选择框样式
function delCheckLeaderCSS(obj) {
    if ($(obj).prev().prev().is("span") && $(obj).prev().prev().prev().is("select")) {
        $(obj).prev().prev().remove();
        $(obj).remove();
    } else if ($(obj).prev().prev().is("span") && $(obj).prev().prev().prev().is("span")) {
        $(obj).prev().prev().remove();
    }
    if ($(obj).prev().prev().hasClass("firstcheckleader")) {
        $(obj).remove();
    }
    if ($(obj).prev().prev().hasClass("casetype_executor")) {
    $(obj).remove();
    }
}

// 获取审核人名单,设置(指定审核人，工单处理人)下拉选择框
function getCheckLeader(obj,type) {
    $.ajax({
        url: '/users/get_user/',
        type: "POST",
        dataType: "json",
        data: {'oper': "getUsers"},
        error: function () {
            if (type === 'check') {
                obj.parent().html((obj.parent().hasClass('firstcheckleader') ? '' : '<span class="glyphicon glyphicon-arrow-right"></span>') + '<select class="select2 checkleader" style="width:140px" ><option value="0">--选择指定审核人--</option></select>');
            } else {
                obj.parent().html((obj.parent().hasClass('casetype_executor') ? '' : '<span class="glyphicon glyphicon-arrow-right"></span>') + '<select class="executor" style="width:140px" ><option value="0">--选择工单处理人--</option></select>');

            }
        },
        success: function (data) {

            var oplist = new Array();
            for (key_num in data['data']) {
                oplist.push('<option value="' + data['data'][key_num]['id'] + '">' + data['data'][key_num]['cnname'] + '(' + data['data'][key_num]['name'] + ')</option>');
            }

            if (type === 'check') {
                obj.parent().html((obj.parent().hasClass('firstcheckleader') ? '' : '<span class="glyphicon glyphicon-arrow-right"></span>') + '<select class="select2 checkleader" style="width:140px" ><option value="0">--选择指定审核人--</option>' + oplist.join('') + '</select>');

            } else {
                obj.parent().html((obj.parent().hasClass('casetype_executor') ? '' : '<span class="glyphicon glyphicon-arrow-right"></span>') + '<select class="executor" style="width:140px" ><option value="0">--选择工单处理人--</option>' + oplist.join('') + '</select>');

            }
            oplist = null;

        }
    });
}

//获取指定审核人名单
function changeCheckLeader(obj) {
    if ($(obj).val() == "-2") {
        getCheckLeader($(obj), 'check');
    }
}

//获取指定执行人名单
function changeExecutor(obj) {
    if ($(obj).val() == "-2") {
        getCheckLeader($(obj), 'executor');
    }
}

//关闭 modalCaseTypeOperating 时触发
$('#modalCaseTypeOperating').on('hide.bs.modal', function (e) {
    document.getElementById('casetype_name').value = "";
    document.getElementById('casetype_id').value = "-1";
    //$("#casetype_executor").find('option[selected="selected"]').removeAttr("selected");
    //executor
    //$("#casetype_executor").empty();
    $(".casetype_executor").each(function () {
        $(this).remove();
    });

    $(".moreexecutor").each(function () {
        $(this).remove();
    });
    $("#delexecutor").remove();
    $("#addExector").before('<span class="casetype_executor"><select class="executor" name="casetype_executor" id="casetype_executor" style="width:140px" onchange="changeExecutor(this);"><option value="-1">默认上级</option><option value = "-2">指定人选</option></select></span>');

    //$("#firstcheckleader").remove();
    $(".firstcheckleader").each(function () {
        $(this).remove();
    });

    $(".morecheckleader").each(function () {
        $(this).remove();
    });

    $(".checkleader").each(function () {
        $(this).remove();
    });

    $("#delcheckleader").remove();
    $("#addcheckleader").before('<span class="firstcheckleader"><select class="select2 checkleader" name="firstcheckleader" id="firstcheckleader" style="width:140px" onchange="changeCheckLeader(this);"><option value="-1">默认上级</option><option value = "-2">指定人选</option></select></span>');
})


//关闭 modalCaseTypeDelete 时触发
$('#modalCaseTypeDelete').on('hide.bs.modal', function (e) {
    //Do something
})


// 提交表单数据
function addCaseType() {

    var var_casetype_id = $("#casetype_id").val();
    if (var_casetype_id == '-1') {
        var post_type = "addCaseType";
    } else {
        var post_type = "editCaseType";
    }

   var  user_id = $("#user_id").val();

    const var_casetype_name = $("#casetype_name").val();
    if (var_casetype_name == '') {
        alert("请填写工单类型名称");
        $("#casetype_name").focus();
        return false;
    }

    // const casetype_executor_val = $("#casetype_executor").find("option:selected").val();
    // //var casetype_executor_text = $("#casetype_executor").find("option:selected").text();
    // if (casetype_executor_val == '0') {
    //     alert("请选择处理人");
    //     $("#casetype_executor").focus();
    //     return false;
    // }

    //工单是否启用
    const casetype_status_val = $("#casetype_status").find("option:selected").val();

    let count = 0;
    //获取审核人列表
    const checkleaderarr = [];
    $(".checkleader").each(function () {
        if ($(this).is('select')) {
            //alert($(this).find("option:selected").text())
            //alert($(this).find("option:selected").val())
            var tmp_checkleader_var = $(this).find("option:selected").val()
            //var tmp_checkleader_text = $(this).find("option:selected").text()
            if (tmp_checkleader_var == '0') {
                alert("请选择指定审核人");
                $(this).focus();
                count = 1;
                return false;
            }
            checkleaderarr.push(tmp_checkleader_var);
        }
    });
    if ( count == 1 ){
        count = 0;
        return false;
        }
    let var_checkleader = checkleaderarr.join(',');
    //alert(var_checkleader);
    //alert(var_casetype_name+casetype_executor_val+var_checkleader);

    //工单处理人列表
    const executorarr = [];
    $(".executor").each(function () {
        if ($(this).is('select')) {
            //alert($(this).find("option:selected").text())
            //alert($(this).find("option:selected").val())
            const tmp_executor_var = $(this).find("option:selected").val();
            //var tmp_executor_text = $(this).find("option:selected").text()
            if (tmp_executor_var == '0') {
                alert("请选择工单处理人");
                $(this).focus();
                count = 1;
                return false;
            }
            executorarr.push(tmp_executor_var);
        }

    });
    if ( count == 1 ){
        count = 0;
        return false;
        }
    let casetype_executor_val = executorarr.join(',');
    //alert(casetype_executor_val)

    $.ajax({
        url: '/ticket/ticket_type/',
        type: "POST",
        dataType: "json",
        data: {
            'oper': post_type,
            'casetype_id': var_casetype_id,
            'name': var_casetype_name,
            'type_form': 1,
            'exec_model': casetype_executor_val,
            'audit_model': var_checkleader,
            'status': casetype_status_val,

        },
        success: function (response) {
                            $('#modalCaseTypeOperating').modal('hide');
                            if (response["code"] == "200") {
                                window.wxc.xcConfirm(response["msg"], window.wxc.xcConfirm.typeEnum.success);
                                location.reload();
                            } else {
                                window.wxc.xcConfirm(response["msg"], window.wxc.xcConfirm.typeEnum.error);
                            }
                        },
        error: function (response) {
            window.wxc.xcConfirm("请求数据错误！", window.wxc.xcConfirm.typeEnum.error);
        },
    });
}