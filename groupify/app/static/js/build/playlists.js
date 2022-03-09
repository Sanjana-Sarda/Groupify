var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var Playlists = function (_React$Component) {
  _inherits(Playlists, _React$Component);

  function Playlists() {
    _classCallCheck(this, Playlists);

    var _this = _possibleConstructorReturn(this, (Playlists.__proto__ || Object.getPrototypeOf(Playlists)).call(this));

    _this.state = {};
    return _this;
  }

  _createClass(Playlists, [{
    key: "render",
    value: function render() {
      return React.createElement(
        "div",
        {
          style: {
            position: "absolute",
            top: 0,
            left: 0,
            width: "100vw",
            height: "100vh",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            flexDirection: "column"
          }
        },
        React.createElement(
          "div",
          { "class": "playlist-display" },
          React.createElement(
            "h2",
            { style: { fontSize: "20px", align: "center" } },
            "Enjoy your group playlist!"
          )
        ),
        React.createElement("br", null),
        React.createElement("iframe", {
          src: "https://open.spotify.com/embed/playlist/" + getCookie("playlist_id"),
          width: "600",
          height: "400",
          align: "middle",
          frameBorder: "0",
          allowtransparency: "true",
          allow: "encrypted-media"
        })
      );
    }
  }]);

  return Playlists;
}(React.Component);

ReactDOM.render(React.createElement(Playlists, null), document.getElementById("display-playlist"));