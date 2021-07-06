function pagination(url, method, params) {
    $.ajax({
        url: url,
        method: method,
        data: params,
        dataType: "json",
    }).success(function (resp) {
        let total = resp.pagination.total;
        let size = resp.pagination.size;
        let start = resp.pagination.start;
        $('#pagination_total').text(total);
        $('#pagination_page').text((start / size) + 1);
        let div = ''
    })

    return ajax;
}