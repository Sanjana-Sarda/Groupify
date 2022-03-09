var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var Home = function (_React$Component) {
  _inherits(Home, _React$Component);

  function Home() {
    _classCallCheck(this, Home);

    var _this = _possibleConstructorReturn(this, (Home.__proto__ || Object.getPrototypeOf(Home)).call(this));

    _this.state = {};
    return _this;
  }

  _createClass(Home, [{
    key: "componentDidMount",
    value: function componentDidMount() {
      if (getCookie("username")) {
        this.setState({ username: getCookie("username"), loggedIn: true });
      }
    }
  }, {
    key: "render",
    value: function render() {
      if (this.state.loggedIn) {
        return React.createElement(
          "div",
          null,
          React.createElement(TopBar, null),
          React.createElement(
            "div",
            { className: "welcome-box" },
            React.createElement(
              "h1",
              { style: { marginBottom: "15px", color: "#6800EC" } },
              "Hi, ",
              this.state.username,
              "!"
            ),
            React.createElement("br", null),
            React.createElement(Functions, null)
          )
        );
      } else {
        return React.createElement(
          "div",
          null,
          React.createElement(TopBar, { left: "none" }),
          React.createElement(
            "div",
            { className: "center" },
            React.createElement(
              "h1",
              { style: { color: "black", fontSize: "40px", align: "center" } },
              "Welcome to Groupify!"
            ),
            React.createElement(
              "h2",
              {
                style: {
                  color: "black",
                  fontSize: "20px",
                  align: "center"
                }
              },
              React.createElement(
                "em",
                null,
                "Get ready to create the group playlist with songs everyone will love"
              )
            ),
            React.createElement("br", null),
            React.createElement(LoginButton, { className: "noselect", text: "Log in with Spotify" })
          )
        );
      }
    }
  }]);

  return Home;
}(React.Component);

ReactDOM.render(React.createElement(Home, null), document.getElementById("home-mount-point"));