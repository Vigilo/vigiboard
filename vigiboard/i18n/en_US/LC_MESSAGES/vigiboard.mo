��    �      4              L     M     ^     k       3   �  2   �  H   �  0   @  x   q  �   �  S  �  �  �  $   �  �     
  �  R        Z     g  
   n     y  
   �     �  	   �     �     �  &   �     �     �  #        1  i   P     �     �     �     �     �     �       .        L     j  -   y  !   �     �  �  �     j     �     �     �     �     �     �     �     �  �   �     z     �     �  I   �       &   +     R     a     u     �  
   �     �     �  +   �                    )     1     K     c     |     �     �     �     �     �  �   �     f     �     �     �     �     �  7   �  =        S  
   Y     d     i     p     |     �     �     �     �     �     �  	   �     �     �     �           #     &      ?!     Q!  Q   e!     �!     �!     �!     �!     �!  	   �!     �!     "     "     '"  /   C"     s"     z"     �"     �"     �"  B   �"     #     !#     9#  
   B#     M#     _#     o#     x#     �#     �#     �#     �#  C   �#     $  "    $     C$     I$  M   f$  P   �$  �   %     �%  �  &  �   �(  �   �)     9*  N   >*     �*  
   �*  \   �*  t   +     y+  7   ~+     �+     �+  	   �+     �+  	   �+     �+     ,     ,     ,  M   5,  '   �,  R   �,     �,    -     %.     B.     G.  �   M.  :   �.     5/  �   A/     0     0     !0     &0     /0     60     G0     P0  >   V0  #   �0     �0     �0     �0  	   �0     �0     	1  �   1    �1     3     &3     +3     B3  ^  N3     �4     �4     �4      �4     �4  	   5     5  K  5     i6     q6     v6     �6     �6     �6    �6     �7     �7     �7     �7     �7  �  �7     �9     �9     �9     �9  3   �9  2    :  H   3:  0   |:  x   �:  �   &;  S  �;  �  9=  $   .?  �   S?  
  8@  R   CA     �A     �A  
   �A     �A  
   �A     �A  	   �A     �A     �A  &   �A      B     :B  #   IB     mB  i   �B     �B     �B     C     C     C     5C     SC  .   YC  	   �C     �C  -   �C  !   �C     �C  �  �C     �E     �E     �E     �E     �E     �E     �E     F     F  �   F     �F     �F     �F  I   �F     3G  &   SG     zG     �G     �G     �G  
   �G     �G     �G  +   �G     *H     0H     EH     QH     YH     sH     �H     �H     �H     �H     �H     �H     �H  �   I     �I     �I     �I     �I     �I     �I  7   J  =   =J     {J  
   �J     �J     �J     �J     �J     �J     �J     �J     �J     �J     �J  	   K     K     !K     &K     3K     KK    NK     gL     yL  Q   �L     �L     �L     �L     �L     M  	   M     M     5M     BM     OM  /   kM     �M     �M     �M     �M     �M  B   �M     0N     IN     aN  
   jN     uN     �N     �N     �N     �N     �N     �N     �N  C   �N     CO  "   HO     kO     qO  M   �O  P   �O  �   -P     'Q  �  <Q  �   T  �   �T     aU  N   fU     �U  
   �U  \   �U  t   ,V     �V  7   �V     �V     �V  	   �V     W  	   W     W     +W     3W     EW  M   ]W  '   �W  R   �W     &X    8X     MY     jY     oY  �   uY  :   "Z     ]Z  �   iZ     =[     D[     I[     N[     W[     ^[     o[     x[  >   ~[  #   �[     �[     �[     \  	   \     %\     1\  �   =\    ']     ?^     N^     S^     j^  ^  v^     �_     �_     �_      �_     `  	   4`     >`  K  E`     �a     �a     �a     �a     �a     �a    �a     �b     �b     �b     c     c   " file under the "strftime()" ${sidebar_bottom()} ${sidebar_top()} (recent ticket updates, svn checkins, wiki changes) (still useful, although a lot has changed for TG2) ), 
            the command went through the RootController class to the - Read everything in the Getting Started section - The
             sidebars (navigation areas on the right side of the page) are 
             generated as two separate - The 
            "footer.html" block is simple, but also utilizes a special 
            "replace" method to set the current YEAR in the footer copyright 
            message. The code is: - The 
            "header.html" template contains the HTML code to display the 
            'header': The blue gradient, TG2 logo, and some site text at the 
            top of every page it is included on. When the "about.html" template 
            is called, it includes this "header.html" template (and the others) 
            with a - The 
            "master.html" template is called last, by design.  The "master.html" 
            template controls the overall design of the page we're looking at, 
            calling first the "header" py:def macro, then the putting everything 
            from this "about.html" template into the "content" div, and 
            then calling the "footer" macro at the end.  Thus the "master.html" 
            template provides the overall architecture for each page in this 
            site. . 
            It means replace this . 
            Take 'about' page for example, each reusable templates generating 
            a part of the page. We'll cover them in the order of where they are 
            found, listed near the top of the about.html template . This controller is protected globally.
    Instead of having a @require decorator on each method, we have set an allow_only attribute at the class level. All the methods in this controller will
    require the same level of access. You need to be manager to access . This one is protected by a different set of permissions.
    You will need to be /controllers /model /templates 1 Minute 10 Minutes 30 Secondes 5 Minutes <br />[Duration] <span /> <span py:replace="now.strftime('%Y')"> <span py:replace="page"/> <xi:include /> A %(error_code)d Error has Occurred A quick guide to this TG2 site A web page viewed by user could be constructed by single or 
            several reusable templates under About About this page Accueil Admin All objects from locals(): Another protected resource is Apply Architectural basics of a quickstart TG2 site. Aucun évènement disponible. Authentication Authentication & Authorization in a TG2 site. Back to your Quickstart Home page Barre Outils But why then shouldn't we call it first?  Isn't it the most 
            important?  Perhaps, but that's precisely why we call it LAST. 
            The "master.html" template needs to know where to find everything 
            else, everything that it will use in py:def macros to build the
             page.  So that means we call the other templates first, and then 
             call "master.html". Change to Acknowledged Change to Closed Change to None Code my data model Code your data model Contact Critical Current State: Date Decide your URLs, Program your controller methods, Design your 
            templates, and place some static files (CSS and/or JavaScript). Default font size Design my URL structure Design your URL architecture Design your data model, Create the database, and Add some bootstrap data. Detailed history for this event Detailed history for this host/service Developing TG2 Distribute your app Déconnexion Détails sur l'évènement Edit Event Edit all selected events Editer cet élément Editer tous les évènements sélectionnés Error Error %(error_code)d Error in DB Filtrer Follow these instructions For checking out a copy For installing your copy Get Started with TG2 Good luck with TurboGears 2! Historique de l'élément History Home Host If you have access to this page, this means you have enabled authentication and authorization
    in the quickstart to create your project. In case you need a quick look Initial Initial State: Join the TG Mail List Join the TG-Trunk Mail List Large font size Learning TurboGears 2.0: Quick guide to authentication. Learning TurboGears 2.0: Quick guide to the Quickstart pages. Login Login Form Logo Logout Maintenance Major Medium font size Minor Mode recherche, More TG2 Documents Never No access to this event No change Nombre d'occurrences None Now Viewing: Now try to visiting the OK Oh, and in sidebar_top we've added a dynamic menu that shows the 
            link to this page at the top when you're at the "index" page, and 
            shows a link to the Home (index) page when you're here.  Study the 
            "sidebars.html" template to see how we used Only for managers Only for the editor Only managers are authorized to visit this method. You will need to log-in using: Output Page 0 Page précédente Page suivante Pages Password: Powered by TurboGears 2 Presentation Précédente Reuse the web page elements Sample Template, for looking at template locals Search Search Event Service Service Type<br />Service Name Service de haut niveau Showing rows %(id_first_row)d to %(id_last_row)d of %(total_rows)d Showing rows 0 to 0 of 0 Statut de l'évènement Suivante Suppressed Sélectioner tout TG Dev timeline TG1 docs TG2 Documents TG2 SVN repository TG2 Trac tickets TG2 Trac's svn view Tableau des évènements Test your source, Generate project documents, Build a distribution. Text Thank you for choosing TurboGears. The " The Python web metaframework The TG2 quickstart command produces this basic TG site.  Here's how it works. The last kind of protected resource in this quickstarted app is a full so called The paster command will have created a few specific controllers for you. But before you
    go to play with those controllers you'll need to make sure your application has been
    properly bootstapped.
    This is dead easy, here is how to do this: There is no history. There's more to the "master.html" template... study it to see how 
           the <title> tags and static JS and CSS files are brought into 
           the page.  Templating with Genshi is a powerful tool and we've only 
           scratched the surface.  There are also a few little CSS tricks 
           hidden in these pages, like the use of a "clearingdiv" to make 
           sure that your footer stays below the sidebars and always looks 
           right.  That's not TG2 at work, just CSS.  You'll need all your 
           skills to build a fine web app, but TG2 will make the hard parts 
           easier so that you can concentrate more on good design and content 
           rather than struggling with mechanics. This is, of course, also exactly how the header and footer 
            templates are also displayed in their proper places, but we'll 
            cover that in the "master.html" template below. Those Python methods are responsible to create the dictionary of
             variables that will be used in your web views (template). Time To change the comportement of this setup-app command you just need to edit the Trouble Ticket TurboGears TurboGears 2 is rapid web application development toolkit designed to make your life easier. TurboGears is a open source front-to-back web development
      framework written in Python. Copyright (c) 2005-2008 Type URL. You will be challenged with a login/password form. Updated successfully User Username: Value Vigiboard We hope to see you soon! Welcome Welcome back, %s! Welcome to TurboGears 2 Welcome to TurboGears 2.0, standing on the 
  shoulders of giants, since 2007 What's happening now in TG2 development When you want a model for storing favorite links or wiki content, 
            the Wrong credentials You can build a dynamic site without any data model at all. There 
            still be a default data-model template for you if you didn't enable 
            authentication and authorization in quickstart. If you enabled
            it, you got auth data-model made for you. You need to be authenticated [TT] about and it uses the variable "now" that was passed 
            in with the dictionary of variables.  But because "now" is a 
            datetime object, we can use the Python blocks 
             in the "sidebars.html" template.  The cliquer ici construct is best thought of as a "macro" code... a simple way to 
             separate and reuse common code snippets.  All it takes to include 
             these on the "about.html" page template is to write detail down edit edit_all editor editor_user_only editpass file. folder has your URLs.  When you 
            called this url ( folder in your site is ready to go. footer.html for TG2 discuss/dev for general TG use/topics for that. header.html in progress in the page where they are wanted.  CSS styling (in 
        "/public/css/style.css") floats them off to the right side.  You can 
        remove a sidebar or add more of them, and the CSS will place them one 
        atop the other. inside your application's folder and you'll get a database setup (using the preferences you have
    set in your development.ini file). This database will also have been prepopulated with some
    default logins/passwords so that you can test the secured controllers and methods. login: manager logo manage_permission_only master.html method with the "replace" 
            call to say "Just Display The Year Here".  Simple, elegant; we 
            format the date display in the template (the View in the 
            Model/View/Controller architecture) rather than formatting it in 
            the Controller method and sending it to the template as a string 
            variable. method. or password: managepass paster setup-app development.ini pour revenir au mode initial. py:choose py:def region with the contents found in the variable 'page' that has 
            been sent in the dictionary to this "about.html" template, and is 
            available through that namespace for use by this "header.html" 
            template.  That's how it changes in the header depending on what 
            page you are visiting. root.py secc secc/some_where secure controller sidebars.html statut tag, part of 
            the Genshi templating system. The "header.html" template is not a 
            completely static HTML -- it also dynamically displays the current 
            page name with a Genshi template method called "replace" with the 
            code: to be able to access it. up v websetup.py with a password of Project-Id-Version: vigiboard 0.1
Report-Msgid-Bugs-To: EMAIL@ADDRESS
POT-Creation-Date: 2009-07-06 11:19+0200
PO-Revision-Date: 2009-09-03 14:11+0200
Last-Translator: Thomas ANDREJAK <thomas.andrejak@c-s.fr>
Language-Team: en_US <LL@li.org>
Plural-Forms: nplurals=2; plural=(n != 1)
MIME-Version: 1.0
Content-Type: text/plain; charset=utf-8
Content-Transfer-Encoding: 8bit
Generated-By: Babel 0.9.4
 " file under the "strftime()" ${sidebar_bottom()} ${sidebar_top()} (recent ticket updates, svn checkins, wiki changes) (still useful, although a lot has changed for TG2) ), 
            the command went through the RootController class to the - Read everything in the Getting Started section - The
             sidebars (navigation areas on the right side of the page) are 
             generated as two separate - The 
            "footer.html" block is simple, but also utilizes a special 
            "replace" method to set the current YEAR in the footer copyright 
            message. The code is: - The 
            "header.html" template contains the HTML code to display the 
            'header': The blue gradient, TG2 logo, and some site text at the 
            top of every page it is included on. When the "about.html" template 
            is called, it includes this "header.html" template (and the others) 
            with a - The 
            "master.html" template is called last, by design.  The "master.html" 
            template controls the overall design of the page we're looking at, 
            calling first the "header" py:def macro, then the putting everything 
            from this "about.html" template into the "content" div, and 
            then calling the "footer" macro at the end.  Thus the "master.html" 
            template provides the overall architecture for each page in this 
            site. . 
            It means replace this . 
            Take 'about' page for example, each reusable templates generating 
            a part of the page. We'll cover them in the order of where they are 
            found, listed near the top of the about.html template . This controller is protected globally.
    Instead of having a @require decorator on each method, we have set an allow_only attribute at the class level. All the methods in this controller will
    require the same level of access. You need to be manager to access . This one is protected by a different set of permissions.
    You will need to be /controllers /model /templates 1 Minute 10 Minutes 30 Secondes 5 Minutes <br />[Duration] <span /> <span py:replace="now.strftime('%Y')"> <span py:replace="page"/> <xi:include /> A %(error_code)d Error has Occurred A quick guide to this TG2 site A web page viewed by user could be constructed by single or 
            several reusable templates under About About this page Accueil Admin All objects from locals(): Another protected resource is Apply Architectural basics of a quickstart TG2 site. No events Authentication Authentication & Authorization in a TG2 site. Back to your Quickstart Home page Barre Outils But why then shouldn't we call it first?  Isn't it the most 
            important?  Perhaps, but that's precisely why we call it LAST. 
            The "master.html" template needs to know where to find everything 
            else, everything that it will use in py:def macros to build the
             page.  So that means we call the other templates first, and then 
             call "master.html". Change to Acknowledged Change to Closed Change to None Code my data model Code your data model Contact Critical Current State: Date Decide your URLs, Program your controller methods, Design your 
            templates, and place some static files (CSS and/or JavaScript). Default font size Design my URL structure Design your URL architecture Design your data model, Create the database, and Add some bootstrap data. Detailed history for this event Detailed history for this host/service Developing TG2 Distribute your app Déconnexion Détails sur l'évènement Edit Event Edit all selected events Editer cet élément Editer tous les évènements sélectionnés Error Error %(error_code)d Error in DB Filtrer Follow these instructions For checking out a copy For installing your copy Get Started with TG2 Good luck with TurboGears 2! Historique de l'élément History Home Host If you have access to this page, this means you have enabled authentication and authorization
    in the quickstart to create your project. In case you need a quick look Initial Initial State: Join the TG Mail List Join the TG-Trunk Mail List Large font size Learning TurboGears 2.0: Quick guide to authentication. Learning TurboGears 2.0: Quick guide to the Quickstart pages. Login Login Form Logo Logout Maintenance Major Medium font size Minor Mode recherche, More TG2 Documents Never No access to this event No change Nombre d'occurrences None Now Viewing: Now try to visiting the OK Oh, and in sidebar_top we've added a dynamic menu that shows the 
            link to this page at the top when you're at the "index" page, and 
            shows a link to the Home (index) page when you're here.  Study the 
            "sidebars.html" template to see how we used Only for managers Only for the editor Only managers are authorized to visit this method. You will need to log-in using: Output Page 0 Page précédente Page suivante Pages Password: Powered by TurboGears 2 Presentation Précédente Reuse the web page elements Sample Template, for looking at template locals Search Search Event Service Service Type<br />Service Name Service de haut niveau Showing rows %(id_first_row)d to %(id_last_row)d of %(total_rows)d Showing rows 0 to 0 of 0 Statut de l'évènement Suivante Suppressed Sélectioner tout TG Dev timeline TG1 docs TG2 Documents TG2 SVN repository TG2 Trac tickets TG2 Trac's svn view Tableau des évènements Test your source, Generate project documents, Build a distribution. Text Thank you for choosing TurboGears. The " The Python web metaframework The TG2 quickstart command produces this basic TG site.  Here's how it works. The last kind of protected resource in this quickstarted app is a full so called The paster command will have created a few specific controllers for you. But before you
    go to play with those controllers you'll need to make sure your application has been
    properly bootstapped.
    This is dead easy, here is how to do this: There is no history. There's more to the "master.html" template... study it to see how 
           the <title> tags and static JS and CSS files are brought into 
           the page.  Templating with Genshi is a powerful tool and we've only 
           scratched the surface.  There are also a few little CSS tricks 
           hidden in these pages, like the use of a "clearingdiv" to make 
           sure that your footer stays below the sidebars and always looks 
           right.  That's not TG2 at work, just CSS.  You'll need all your 
           skills to build a fine web app, but TG2 will make the hard parts 
           easier so that you can concentrate more on good design and content 
           rather than struggling with mechanics. This is, of course, also exactly how the header and footer 
            templates are also displayed in their proper places, but we'll 
            cover that in the "master.html" template below. Those Python methods are responsible to create the dictionary of
             variables that will be used in your web views (template). Time To change the comportement of this setup-app command you just need to edit the Trouble Ticket TurboGears TurboGears 2 is rapid web application development toolkit designed to make your life easier. TurboGears is a open source front-to-back web development
      framework written in Python. Copyright (c) 2005-2008 Type URL. You will be challenged with a login/password form. Updated successfully User Username: Value Vigiboard We hope to see you soon! Welcome Welcome back, %s! Welcome to TurboGears 2 Welcome to TurboGears 2.0, standing on the 
  shoulders of giants, since 2007 What's happening now in TG2 development When you want a model for storing favorite links or wiki content, 
            the Wrong credentials You can build a dynamic site without any data model at all. There 
            still be a default data-model template for you if you didn't enable 
            authentication and authorization in quickstart. If you enabled
            it, you got auth data-model made for you. You need to be authenticated [TT] about and it uses the variable "now" that was passed 
            in with the dictionary of variables.  But because "now" is a 
            datetime object, we can use the Python blocks 
             in the "sidebars.html" template.  The cliquer ici construct is best thought of as a "macro" code... a simple way to 
             separate and reuse common code snippets.  All it takes to include 
             these on the "about.html" page template is to write detail down edit edit_all editor editor_user_only editpass file. folder has your URLs.  When you 
            called this url ( folder in your site is ready to go. footer.html for TG2 discuss/dev for general TG use/topics for that. header.html in progress in the page where they are wanted.  CSS styling (in 
        "/public/css/style.css") floats them off to the right side.  You can 
        remove a sidebar or add more of them, and the CSS will place them one 
        atop the other. inside your application's folder and you'll get a database setup (using the preferences you have
    set in your development.ini file). This database will also have been prepopulated with some
    default logins/passwords so that you can test the secured controllers and methods. login: manager logo manage_permission_only master.html method with the "replace" 
            call to say "Just Display The Year Here".  Simple, elegant; we 
            format the date display in the template (the View in the 
            Model/View/Controller architecture) rather than formatting it in 
            the Controller method and sending it to the template as a string 
            variable. method. or password: managepass paster setup-app development.ini pour revenir au mode initial. py:choose py:def region with the contents found in the variable 'page' that has 
            been sent in the dictionary to this "about.html" template, and is 
            available through that namespace for use by this "header.html" 
            template.  That's how it changes in the header depending on what 
            page you are visiting. root.py secc secc/some_where secure controller sidebars.html statut tag, part of 
            the Genshi templating system. The "header.html" template is not a 
            completely static HTML -- it also dynamically displays the current 
            page name with a Genshi template method called "replace" with the 
            code: to be able to access it. up v websetup.py with a password of 