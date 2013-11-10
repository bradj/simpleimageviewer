(function () {

    function Carousel() {
        if (window.innerWidth <= 768) return;

        var that = this;
        this.h = function() { return window.innerHeight; }
        this.idx = null;
        this.img = document.getElementsByClassName('carousel')[0].getElementsByTagName('img')[0];
        this.progress = document.querySelector('.showprogress');
        this.imgcontainer = document.getElementsByClassName('imgcontainer');

        var c = document.querySelector('.carousel');
        c.onclick = function(evt) {
            if (!$(c).hasClass('hidden')) {
                $(c).addClass('hidden');
                that.img.src = '';
                that.img.parentNode.setAttribute('href', '#');
            }
        };

        var list = document.querySelectorAll('.image > a');
        for (var ii = 0, length = list.length; ii < length; ii++) {
            list[ii].onclick = function (evt) {
                that.setSource(evt.target.parentNode.getAttribute('href'));
                that.idx = evt.target.parentNode.parentNode;
                $(c).removeClass('hidden');
                return false;
            };
        }

        document.querySelector('.carousel a').onclick = function(evt) {
            evt.stopPropagation();
        };

        document.querySelector('.carouselbutton:first-child').onclick = function(evt) {
            evt.stopPropagation();
            that.rotateCarousel(true);
        };

        document.querySelector('.carouselbutton:last-child').onclick = function(evt) {
            evt.stopPropagation();
            that.rotateCarousel(false);
        };

        this.rotateCarousel = function(left) {
            if (left && (!that.idx || !that.idx.previousSibling)) return;
            if (!left && (!that.idx || !that.idx.nextSibling)) return;

            that.idx = left ? that.idx.previousSibling : that.idx.nextSibling;
            that.setSource(that.idx.childNodes[0].getAttribute('href'));
        };

        this.setSource = function(src) {
            var image = new Image();
            $(that.progress).toggleClass('hidden');
            $(that.imgcontainer).toggleClass('hidden');
            image.onload = function(evt) {
                if (image.height > image.width) {
                    if ($(that.img).hasClass('img-responsive'))
                        $(that.img).removeClass('img-responsive');
                    that.img.style.height =  that.h() - 100 + 'px';
                }
                else {
                    if (!$(that.img).hasClass('img-responsive'))
                        $(that.img).addClass('img-responsive');
                    that.img.style.height = 'auto';
                }
                
                that.img.src = src;
                that.img.parentNode.setAttribute('href', that.img.src);
                $(that.progress).toggleClass('hidden');
                $(that.imgcontainer).toggleClass('hidden');
            };
            that.img.src = '';
            image.src = src;
        };
    };

    window.onload = function() {
        console.log('loaded');

        var c = new Carousel();
    };

})();