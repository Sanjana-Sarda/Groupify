var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var PartyMember = function (_React$Component) {
    _inherits(PartyMember, _React$Component);

    function PartyMember() {
        _classCallCheck(this, PartyMember);

        var _this = _possibleConstructorReturn(this, (PartyMember.__proto__ || Object.getPrototypeOf(PartyMember)).call(this));

        _this.state = { members: [getCookie('username')], songLoaded: false, membersLoaded: false };
        _this.token = getCookie('token');
        _this.server = io();
        return _this;
    }

    _createClass(PartyMember, [{
        key: 'updateListening',
        value: function updateListening(data) {
            var _this2 = this;

            if (!data.playing) {
                fetch('https://api.spotify.com/v1/me/player/pause', {
                    method: 'PUT',
                    headers: {
                        Authorization: 'Bearer ' + this.token
                    }
                }).then(function (res) {
                    return res.text();
                }).then(function (dat) {
                    if (dat != '') {
                        var data1 = JSON.parse(dat);
                        _this2.checkForErrors(data, data1);
                    }
                });
            } else {
                var bodyData = { uris: [data.song_uri], position_ms: data.time };
                fetch('https://api.spotify.com/v1/me/player/play', {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        Authorization: 'Bearer ' + this.token
                    },
                    body: JSON.stringify(bodyData)
                }).then(function (res) {
                    return res.text();
                }).then(function (dat) {
                    if (dat != '') {
                        var data1 = JSON.parse(dat);
                        _this2.checkForErrors(data, data1);
                    }
                });
            }
        }
    }, {
        key: 'checkForErrors',
        value: function checkForErrors(data, data1) {
            var _this3 = this;

            if (data1.error) {
                if (data1.error.status === 401) {
                    if (data1.error.message === 'The access token expired' || data.error.message === 'Invalid access token') {
                        console.log('refreshing token');
                        refreshToken().then(function (t) {
                            _this3.token = t;
                            _this3.updateListening(data);
                        });
                    }
                }
                if (data1.error.reason) {
                    if (data1.error.reason === "NO_ACTIVE_DEVICE") {
                        console.log('error: no active device');
                        this.setState({ error: 'Error: no active device!!!', errorSub: 'open a Spotify client and start playing a track, then refresh!' });
                        return;
                    }
                    if (data1.errr.reason !== "NO_ACTIVE_DEVICE") {
                        this.setState({ error: null, errorSub: null });
                        return;
                    }
                }
            }
        }
    }, {
        key: 'componentDidMount',
        value: function componentDidMount() {
            var _this4 = this;

            if (!this.token) {
                refreshToken().then(function (t) {
                    _this4.token = t;
                });
            }
            document.cookie = 'party_id=' + window.location.pathname.replace('/party/', '');
            this.server.on('connect', function () {
                _this4.server.emit('join', { username: getCookie('username'), party_id: getCookie('party_id') });
                console.log('joined party');
            });
            this.server.on('join', function (data) {
                if (data.username != getCookie('username')) {
                    console.log(data.username + ' joined the party');
                }
                _this4.setState({ members: data.members, membersLoaded: true });
            });
            this.server.on('leave', function (data) {
                console.log(data.username + ' left the party');
                _this4.setState({ members: data.members, membersLoaded: true });
            });
            this.server.on('update', function (data) {
                if (data.user) {
                    if (data.user === getCookie('username')) {
                        console.log('updating', data);
                        _this4.updateListening(data);
                        _this4.setState({ cover: data.cover, song: data.song, artists: data.artists, songLoaded: true });
                        return;
                    } else {
                        return;
                    }
                }
                console.log('updating', data);
                _this4.updateListening(data);
                _this4.setState({ cover: data.cover, song: data.song, artists: data.artists, songLoaded: true });
            });
            this.server.on('end', function (data) {
                console.log(data);
                _this4.setState({ over: true });
            });
            window.onbeforeunload = function () {
                _this4.leave();
            };
        }
    }, {
        key: 'leave',
        value: function leave() {
            this.server.emit('leave', { username: getCookie('username'), party_id: getCookie('party_id') });
            console.log('left party');
            delete_cookie('party_id');
            window.location.pathname = '/';
        }
    }, {
        key: 'button',
        value: function button() {
            var _this5 = this;

            return React.createElement(
                'a',
                { href: '/', id: 'logout-link', onClick: function onClick() {
                        return _this5.leave();
                    } },
                'Leave Party'
            );
        }
    }, {
        key: 'render',
        value: function render() {
            if (!this.state.over) {
                return React.createElement(
                    'div',
                    null,
                    React.createElement(TopBar, { left: 'leave', elem: this.button() }),
                    React.createElement(
                        'div',
                        { className: 'party-info-container' },
                        this.state.error ? React.createElement(PartyError, { error: this.state.error, sub: this.state.errorSub }) : React.createElement(Playing, { cover: this.state.cover, song: this.state.song, artists: this.state.artists, loaded: this.state.songLoaded }),
                        React.createElement(MemberList, { members: this.state.members, loaded: this.state.membersLoaded })
                    )
                );
            }
            return React.createElement(
                'div',
                null,
                React.createElement(TopBar, { left: 'leave', elem: this.button() }),
                React.createElement(
                    'div',
                    { className: 'center', style: { fontSize: '25px', color: 'white' } },
                    'This party has been ended by the owner'
                )
            );
        }
    }]);

    return PartyMember;
}(React.Component);

ReactDOM.render(React.createElement(PartyMember, null), document.getElementById('party-mount-point'));