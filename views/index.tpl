% rebase('base.tpl')
<div class="uk-card uk-card-default uk-card-body uk-animation-slide-top custom2">
    <h4>go ahead, i'm not looking...<span class="uk-icon uk-icon-image" style="background-image: url(/static/not-looking.png);"></span></h4>
    % if defined('error'):
      <div class="uk-alert-danger uk-text-center uk-alert">
      % for err in error:
          % if err:
          <p>{{err}}</p>
          % end
      % end
      </div>
    % end
<form method="post" action="/create">
    <fieldset class="uk-fieldset">
        <div class="uk-margin">
            <input class="uk-input" style="font-family: 'Fira Code', monospace; font-weight: 500;" type="text" placeholder="password" name="secret">
        </div>
        <p>Delete password after <input type="number" class="uk-input uk-form-width-xsmall" min="1" value="5" step="1" name="days"> days or <input type="number" class="uk-input uk-form-width-spsmall" min="1" value="10" step="1" name="views"> views.
        <p>IP Whitelist:  <input type="text" class="uk-input uk-form-width-medium" name="ip" style="margin-right: 6px"><span uk-icon="question" uk-tooltip="title: Enter an IPv4 or IPv6 Address/CIDR. Also accepts a comma separated list of IPv4/IPv6 Address/CIDR values. Leave blank for none."></span></p>
        <div class="uk-margin">
          <input type="submit" class="uk-button uk-button-primary">
        </div>
    </fieldset>
</form>
</div>
<div uk-alert style="max-width: 900px; padding-top: 30px;">
    <a class="uk-alert-close" uk-close></a>
    <span class="uk-label" style="background-color: rgba(30, 135, 240, .5)"># CHANGELOG</span>
    <p><span class="uk-label" style="background-color: rgba(30, 135, 240, .25)">## [0.0.2] - 2020-07-16</span></p>
    <span uk-icon="chevron-right"></span><b>Added</b> no-referrer policy to /show route.<br>
    <span uk-icon="chevron-right"></span><b>Added</b> better support for mobile clients.<br>
    <p><span class="uk-label" style="background-color: rgba(30, 135, 240, .25)">## [0.0.1] - 2019-11-28</span></p>
    <span uk-icon="chevron-right"></span><b>Added</b> IPv6 Support to pass.sh server.<br>
    <span uk-icon="chevron-right"></span><b>Added</b> support for IP Restricted Viewing<br>
    <span uk-icon="chevron-right"></span><b>Changed</b> Max days is now 90<br>
    <span uk-icon="chevron-right"></span><b>Changed</b> Max views is now 25<br>
</div>
