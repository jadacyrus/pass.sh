% rebase('base.tpl')
<div class="uk-card uk-card-default uk-card-body uk-animation-slide-top custom2">
    <h4>ready to share!</h4>
   <div class="uk-alert-primary uk-alert uk-text-center" style="font-family: 'Fira Code', monospace; font-weight: 500;">
    <p>{{url}}</p>
   </div>
   <hr class="uk-divider-icon">
   <p>Share the above link for access to the secret password. It will expire in <span class="uk-badge">{{days}}</span> days or after <span class="uk-badge">{{views}}</span> views.</p>
   % if defined('ip_list'):
       <p>The above link will only be accessible from the following addresses:</p>
       <ul>
       % for ip in ip_list:
           <li>{{ ip }}</li>
       % end
       </ol>
   % end
</div>
