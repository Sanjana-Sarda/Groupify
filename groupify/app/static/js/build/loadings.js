var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var Loadings = function (_React$Component) {
  _inherits(Loadings, _React$Component);

  function Loadings() {
    _classCallCheck(this, Loadings);

    var _this = _possibleConstructorReturn(this, (Loadings.__proto__ || Object.getPrototypeOf(Loadings)).call(this));

    _this.state = {};
    return _this;
  }

  _createClass(Loadings, [{
    key: 'componentDidMount',
    value: function componentDidMount() {
      this.server = io();
      this.server.on('connect', function () {
        return console.log('connected');
      });
      this.server.on('update', function () {
        console.log('updating');
        location.reload();
      });
    }
  }, {
    key: 'render',
    value: function render() {
      return React.createElement(
        'div',
        null,
        React.createElement(
          'p',
          null,
          'YO'
        )
      );
    }
  }]);

  return Loadings;
}(React.Component);

ReactDOM.render(React.createElement(Loadings, null), document.getElementById("display-loading"));