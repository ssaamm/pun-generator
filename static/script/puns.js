document.isPunsLoading = false;

function setIsPunsLoading() {
    document.isPunsLoading = true;
    document.getElementById('get-button').setAttribute('disabled' , 'disabled');
}

function unsetIsPunsLoading() {
    document.isPunsLoading = false;
    document.getElementById('get-button').removeAttribute('disabled');
}

function get(url, callback, errback) {
    var request = new XMLHttpRequest();
    request.open('GET', url, true);

    request.onload = function() {
        if (this.status >= 200 && this.status < 400) {
            var data = JSON.parse(this.response);
            callback(data);
        } else {
            errback();
        }
    };

    request.onerror = function() {
        errback();
    };

    request.send();
}

function createElement(tag, inner) {
    var textNode = document.createTextNode(inner);
    var tagNode = document.createElement(tag);
    tagNode.appendChild(textNode);
    return tagNode;
}

function onGetPunsClicked(event) {
    if (document.isPunsLoading === true) {
        return;
    }
    setIsPunsLoading();

    var elem = document.getElementById('seed');
    var value = elem.value;
    if (value === '') {
        value = elem.getAttribute('placeholder');
    }

    get('pun?s=' + value, function(data) {
        writePuns(data.puns);
        unsetIsPunsLoading();
    }, function() {
        unsetIsPunsLoading();
    });
}

function writePuns(puns) {
    var list = document.getElementById('puns-list');
    list.innerHTML = '';

    if (puns.length == 0) {
        puns = ['No puns found :('];
    }

    for (var i = 0; i < puns.length; ++i) {
        list.appendChild(createElement('li', puns[i]));
    }
}