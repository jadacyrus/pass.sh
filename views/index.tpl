% rebase('base.tpl')
<div class="uk-card uk-card-default uk-card-body uk-animation-slide-top custom2">
    <h4>go ahead, i'm not looking...<span class="uk-icon uk-icon-image" style="background-image: url(/static/not-looking.png);"></span></h4>
    % if defined('error'):
      <div class="uk-alert-danger uk-text-center uk-alert">
          <p>{{error}}</p>
      </div>
    % end
<form method="post" action="/create">
    <fieldset class="uk-fieldset">

        <div class="uk-margin">
            <input class="uk-input" type="text" placeholder="password" name="secret">
        </div>

        <p>Delete password after <input type="number" class="uk-input uk-form-width-xsmall" min="1" max="5" value="5" step=1" name="days"> days or <input type="number" class="uk-input uk-form-width-spsmall" min="1" max="10" value="10" step=1" name="views"> views.
        <div class="uk-margin">
          <input type="submit" class="uk-button uk-button-primary">
        </div>
    </fieldset>
</form>
</div>
