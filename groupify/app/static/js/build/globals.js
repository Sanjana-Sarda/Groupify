var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

function InviteButton() {
  return React.createElement(
    "span",
    {
      onClick: function onClick() {
        return document.getElementById("invite-dropdown").classList.toggle("show");
      },
      className: "noselect invite-button"
    },
    "Get party code"
  );
}

function InviteDropdown() {
  return React.createElement(
    "div",
    { id: "invite-dropdown", className: "dropdown-content" },
    React.createElement("input", {
      spellCheck: "false",
      readOnly: true,
      id: "link-input",
      value: getCookie("party_id")
    }),
    React.createElement(
      "div",
      {
        onClick: function onClick() {
          document.getElementById("link-input").select();
          document.execCommand("copy");
        },
        className: "copy-button"
      },
      React.createElement("img", { className: "copy-img", src: "/static/images/copy.png" }),
      React.createElement(
        "span",
        null,
        "Copy"
      )
    )
  );
}

function CreatePlaylistButton() {
  return React.createElement(
    "a",
    { className: "create-playlist-button noselect", href: "/create-playlist" },
    "Create Playlist"
  );
}

function CreateButton() {
  return React.createElement(
    "a",
    { className: "create-button noselect", href: "/create" },
    "Create your own party"
  );
}

var JoinBox = function (_React$Component) {
  _inherits(JoinBox, _React$Component);

  function JoinBox() {
    _classCallCheck(this, JoinBox);

    var _this = _possibleConstructorReturn(this, (JoinBox.__proto__ || Object.getPrototypeOf(JoinBox)).call(this));

    _this.state = { classes: "noselect hidden" };
    return _this;
  }

  _createClass(JoinBox, [{
    key: "enterPressed",
    value: function enterPressed(event) {
      var code = event.keyCode || event.which;
      if (code === 13) {
        this.submit();
      }
    }
  }, {
    key: "submit",
    value: function submit() {
      if (this.state.code) {
        window.location.pathname = "/party/" + this.state.code;
      }
    }
  }, {
    key: "updateCode",
    value: function updateCode(event) {
      if (event.target.value) {
        this.setState({ code: event.target.value, classes: "noselect" });
      } else {
        this.setState({ code: null, classes: "noselect hidden" });
      }
    }
  }, {
    key: "render",
    value: function render() {
      var _this2 = this;

      return React.createElement(
        "span",
        null,
        React.createElement("input", {
          onChange: this.updateCode.bind(this),
          onKeyPress: this.enterPressed.bind(this),
          placeholder: "Enter a code",
          className: "code-box"
        }),
        React.createElement(
          "span",
          {
            id: "join-button",
            className: this.state.classes,
            onClick: function onClick() {
              return _this2.submit();
            }
          },
          "join"
        )
      );
    }
  }]);

  return JoinBox;
}(React.Component);

function LoginButton(props) {
  if (props.redirect) {
    return React.createElement(
      "a",
      { className: "login-button", href: "/login?redirect=" + props.redirect },
      props.text
    );
  }
  var link = getCookie("link");
  delete_cookie("link");
  return React.createElement(
    "a",
    { className: "login-button", href: link },
    props.text
  );
}

function TopBar(props) {
  if (props.left === "none") {
    var left = React.createElement("span", null);
  }
  if (!props.left) {
    var left = React.createElement(
      "a",
      { href: "/logout", id: "logout-link" },
      "logout"
    );
  }
  if (props.left === "login") {
    var left = React.createElement(
      "a",
      { href: "/login", id: "logout-link" },
      "login"
    );
  }
  if (props.left === "leave") {
    var left = props.elem;
  }
  if (props.left === "end") {
    var left = React.createElement(
      "a",
      {
        href: "/end/" + window.location.pathname.replace("/party/", ""),
        onClick: function onClick() {
          return props.func();
        },
        id: "logout-link"
      },
      "end party"
    );
  }

  if (props.children) {
    var left = props.children[0];
  }
  return React.createElement(
    "div",
    { className: "topbar noselect" },
    React.createElement(
      "div",
      null,
      React.createElement(
        "a",
        { href: "/", id: "home-link" },
        React.createElement("img", {
          draggable: false,
          src: "/static/images/icon.png",
          height: "150px",
          align: "left"
        })
      ),
      left
    )
  );
}
function Functions() {
  return React.createElement(
    "div",
    null,
    React.createElement(CreateButton, null),
    React.createElement("span", {
      style: { display: "inline-block", width: "20px", height: "20px" }
    }),
    React.createElement(JoinBox, null)
  );
}
function MemberList(props) {
  var members = props.members;
  if (props.loaded) {
    elems = React.createElement(Members, { members: members });
  } else {
    elems = React.createElement(
      "ul",
      { className: "member-list" },
      React.createElement(
        "li",
        null,
        "loading..."
      )
    );
  }
  return React.createElement(
    "div",
    { className: "member-container" },
    React.createElement(
      "div",
      { className: "dropdown" },
      React.createElement(InviteButton, null),
      React.createElement(InviteDropdown, null)
    ),
    React.createElement(
      "h2",
      { className: "noselect", style: { color: "white" } },
      "Members:"
    ),
    React.createElement(
      "div",
      { className: "member-list-container custom-scrollbar" },
      elems
    ),
    React.createElement(CreatePlaylistButton, null)
  );
}

function Members(props) {
  var members = props.members;
  var elems = Object.keys(members).map(function (member) {
    return React.createElement(Member, {
      key: member,
      name: member,
      link: members[member].link,
      owner: members[member].owner
    });
  });
  return React.createElement(
    "ul",
    { className: "member-list" },
    elems
  );
}
function Member(props) {
  if (props.owner) {
    return React.createElement(
      "li",
      { key: props.name },
      React.createElement(
        "a",
        { className: "spotify-link", href: props.link, target: "_blank" },
        props.name
      ),
      React.createElement(
        "span",
        null,
        React.createElement("img", {
          className: "noselect",
          style: { height: "20px", marginLeft: "10px" },
          draggable: false,
          src: "/static/images/crown.png"
        })
      )
    );
  }
  return React.createElement(
    "li",
    { key: props.name },
    React.createElement(
      "a",
      { className: "spotify-link", href: props.link, target: "_blank" },
      props.name
    )
  );
}

function Playing(props) {
  var cover = props.cover;
  var song = props.song;
  var artists = props.artists;
  if (props.loaded) {
    return React.createElement(
      "div",
      { className: "playing-display" },
      React.createElement(
        "h2",
        { className: "noselect", style: { color: "white" } },
        "Currently playing:"
      ),
      React.createElement(Cover, { cover: cover }),
      React.createElement(SongTitle, { song: song }),
      React.createElement(Artists, { artists: artists })
    );
  }
  return React.createElement("div", { className: "playing-display" });
}
function Cover(props) {
  return React.createElement(
    "a",
    { href: props.cover.link, target: "_blank" },
    React.createElement("img", {
      className: "noselect",
      style: { borderRadius: "10px" },
      src: props.cover.img,
      draggable: false
    })
  );
}
function SongTitle(props) {
  return React.createElement(
    "h3",
    null,
    React.createElement(
      "a",
      {
        href: props.song.link,
        target: "_blank",
        className: "spotify-link",
        style: { width: "fit-content" }
      },
      props.song.name
    )
  );
}
function Artists(props) {
  return React.createElement(
    "div",
    null,
    props.artists.map(function (val, i) {
      if (i === props.artists.length - 1) {
        return React.createElement(Artist, { key: i, link: val.link, name: val.name });
      }
      return React.createElement(
        "span",
        null,
        React.createElement(Artist, { key: i, link: val.link, name: val.name }),
        React.createElement(
          "span",
          { style: { color: "white" } },
          ", "
        )
      );
    })
  );
}

function Artist(props) {
  return React.createElement(
    "span",
    null,
    React.createElement(
      "a",
      { className: "spotify-link", href: props.link, target: "_blank" },
      props.name
    )
  );
}
function PartyError(props) {
  return React.createElement(
    "div",
    { className: "playing-display" },
    React.createElement("img", { id: "cat-gif", src: "/static/images/cat.gif" }),
    React.createElement(
      "h3",
      { style: { color: "white" } },
      props.error
    ),
    React.createElement(
      "p",
      { style: { color: "white" } },
      props.sub
    )
  );
}