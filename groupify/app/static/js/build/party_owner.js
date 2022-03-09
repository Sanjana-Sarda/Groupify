var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var PartyOwner = function (_React$Component) {
    _inherits(PartyOwner, _React$Component);

    function PartyOwner() {
        _classCallCheck(this, PartyOwner);

        var _this = _possibleConstructorReturn(this, (PartyOwner.__proto__ || Object.getPrototypeOf(PartyOwner)).call(this));

        _this.state = { members: [getCookie('username')], songLoaded: false, membersLoaded: false };
        _this.token = getCookie('token');
        return _this;
    }

    _createClass(PartyOwner, [{
        key: 'updateListening',
        value: function updateListening() {
            var _this2 = this;

            fetch('https://api.spotify.com/v1/me/player/currently-playing', { headers: {
                    Authorization: 'Bearer ' + this.token
                } }).then(function (res) {
                if (res.status === 204) {
                    console.log('error: no active device');
                    _this2.setState({ error: 'Error: no active device!!!', errorSub: 'open a spotify client and start playing a track!' });
                    return null;
                } else {
                    if (_this2.state.error) {
                        _this2.setState({ error: null, errorSub: null });
                        return _this2.getListening();
                    }
                    return res.json();
                }
            }).then(function (data) {
                if (!data) {
                    return;
                }
                if (data.error) {
                    if (data.error.status === 401) {
                        if (data.error.message === 'The access token expired' || data.error.message === 'Invalid access token') {
                            console.log('refreshing token');
                            refreshToken().then(function (t) {
                                _this2.token = t;
                                _this2.updateListening();
                                console.log('token rereshed');
                            });
                            return;
                        }
                    }
                    if (data.error.message === 'Only valid bearer authentication supported') {
                        console.log('refreshing token');
                        refreshToken().then(function (t) {
                            _this2.token = t;
                            _this2.updateListening();
                            console.log('token rereshed');
                        });
                        return;
                    }
                }
                if (!_this2.data) {
                    _this2.data = data;
                }
                if (_this2.data.item.uri != data.item.uri) {
                    console.log('new', data);
                    data.party_id = getCookie('party_id');
                    data.party_key = getCookie('party_key');
                    _this2.server.emit('update', data);
                    _this2.data = data;
                    _this2.setPlaying(data);
                } else if (_this2.data.is_playing != data.is_playing) {
                    console.log('pause/play', data);
                    data.party_id = getCookie('party_id');
                    data.party_key = getCookie('party_key');
                    _this2.server.emit('update', data);
                    _this2.data = data;
                } else if (Math.round(data.progress_ms / 1000) > Math.round(_this2.data.progress_ms / 1000) + 6) {
                    var today = new Date();
                    var h = today.getHours() * 3600;
                    var s = today.getMinutes() * 60;
                    var new_time = h + s + today.getSeconds();
                    var elapsed = new_time - _this2.time;
                    var skip = Math.round(data.progress_ms / 1000) - Math.round(_this2.data.progress_ms / 1000);
                    if (skip > elapsed + 1) {
                        console.log('forward', data);
                        console.log(skip, elapsed);
                        data.party_id = getCookie('party_id');
                        data.party_key = getCookie('party_key');
                        _this2.server.emit('update', data);
                    }
                    _this2.data = data;
                    _this2.time = new_time;
                } else if (data.progress_ms < _this2.data.progress_ms - 2000) {
                    console.log('back', data);
                    data.party_id = getCookie('party_id');
                    data.party_key = getCookie('party_key');
                    _this2.server.emit('update', data);
                    _this2.data = data;
                }
                if (!_this2.state.song) {
                    _this2.setPlaying(data);
                }
                _this2.data = data;
            });
        }
    }, {
        key: 'getListening',
        value: function getListening(user) {
            var _this3 = this;

            fetch('https://api.spotify.com/v1/me/player/currently-playing', { headers: {
                    Authorization: 'Bearer ' + this.token
                } }).then(function (res) {
                if (res.status === 204) {
                    console.log('error: no active device');
                    _this3.setState({ error: 'Error: no active device!!!', errorSub: 'open a spotify client and start playing a track!' });
                    return null;
                } else {
                    return res.json();
                }
            }).then(function (data) {
                if (!data) {
                    return;
                }
                if (data.error) {
                    if (data.error.status === 401) {
                        if (data.error.message === 'The access token expired' || data.error.message === 'Invalid access token') {
                            console.log('refreshing token');
                            refreshToken().then(function (t) {
                                _this3.token = t;
                                _this3.updateListening();
                                console.log('token refreshed');
                            });
                            return;
                        }
                    }
                }
                console.log('new', data);
                data.party_id = getCookie('party_id');
                data.party_key = getCookie('party_key');
                if (user) {
                    data.user = user;
                }
                _this3.data = data;
                _this3.server.emit('update', data);
                _this3.setPlaying(data);
            });
        }
    }, {
        key: 'setPlaying',
        value: function setPlaying(data) {
            var artists = [];
            var a = data.item.artists;
            for (i = 0; i < a.length; i++) {
                artists.push({ name: a[i].name, link: a[i].external_urls.spotify });
            }
            this.setState({
                cover: { img: data.item.album.images[1].url, link: data.item.album.external_urls.spotify },
                song: { name: data.item.name, link: data.item.album.external_urls.spotify + '?highlight=' + data.item.uri },
                artists: artists,
                songLoaded: true
            });
        }
    }, {
        key: 'componentDidMount',
        value: function componentDidMount() {
            var _this4 = this;

            if (!getCookie('username')) {
                var p = window.location.pathname;
                window.location.pathname = '/login?redirect=' + p;
            }
            this.server = io();
            this.server.on('connect', function () {
                return console.log('connected');
            });
            this.server.on('join', function (data) {
                if (data.username != getCookie('username')) {
                    console.log(data.username + ' joined your party');
                    _this4.getListening(data.username);
                }
                _this4.setState({ members: data.members, membersLoaded: true });
            });
            this.server.on('leave', function (data) {
                if (data.username != getCookie('username')) {
                    console.log(data.username + ' left your party');
                    _this4.setState({ members: data.members, membersLoaded: true });
                }
            });
            this.server.emit('join', { username: getCookie('username'), party_id: getCookie('party_id') });
            var today = new Date();
            var h = today.getHours() * 3600;
            var s = today.getMinutes() * 60;
            this.time = h + s + today.getSeconds();
            this.getListening();
            this.i = setInterval(function () {
                _this4.updateListening();
            }, 1000);
        }
    }, {
        key: 'componentWillUnmount',
        value: function componentWillUnmount() {
            clearInterval(this.i);
        }
    }, {
        key: 'end',
        value: function end() {
            this.server.emit('end', { party_id: getCookie('party_id'), key: getCookie('party_key') });
        }
    }, {
        key: 'render',
        value: function render() {
            var _this5 = this;

            return React.createElement(
                'div',
                null,
                React.createElement(
                    TopBar,
                    { left: 'end' },
                    React.createElement(
                        'a',
                        { href: '/end/' + window.location.pathname.replace('/party/', ''), onClick: function onClick() {
                                return _this5.end();
                            }, id: 'logout-link' },
                        'End Party'
                    ),
                    ';'
                ),
                React.createElement(
                    'div',
                    { className: 'party-info-container' },
                    this.state.error ? React.createElement(PartyError, { error: this.state.error, sub: this.state.errorSub }) : React.createElement(Playing, { cover: this.state.cover, song: this.state.song, artists: this.state.artists, loaded: this.state.songLoaded }),
                    React.createElement(MemberList, { members: this.state.members, loaded: this.state.membersLoaded })
                )
            );
        }
    }]);

    return PartyOwner;
}(React.Component);

ReactDOM.render(React.createElement(PartyOwner, null), document.getElementById('party-mount-point'));