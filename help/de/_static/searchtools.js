/*
 * searchtools.js_t
 * ~~~~~~~~~~~~~~~~
 *
 * Sphinx JavaScript utilities for the full-text search.
 *
 * :copyright: Copyright 2007-2018 by the Sphinx team, see AUTHORS.
 * :license: BSD, see LICENSE for details.
 *
 */


/* Non-minified version JS is _stemmer.js if file is provided */ 
var JSX={};(function(j){function l(b,e){var a=function(){};a.prototype=e.prototype;var c=new a;for(var d in b){b[d].prototype=c}}function H(c,b){for(var a in b.prototype)if(b.prototype.hasOwnProperty(a))c.prototype[a]=b.prototype[a]}function g(a,b,d){function c(a,b,c){delete a[b];a[b]=c;return c}Object.defineProperty(a,b,{get:function(){return c(a,b,d())},set:function(d){c(a,b,d)},enumerable:true,configurable:true})}function I(a,b,c){return a[b]=a[b]/c|0}var C=parseInt;var r=parseFloat;function J(a){return a!==a}var z=isFinite;var y=encodeURIComponent;var x=decodeURIComponent;var w=encodeURI;var u=decodeURI;var t=Object.prototype.toString;var B=Object.prototype.hasOwnProperty;function i(){}j.require=function(b){var a=q[b];return a!==undefined?a:null};j.profilerIsRunning=function(){return i.getResults!=null};j.getProfileResults=function(){return(i.getResults||function(){return{}})()};j.postProfileResults=function(a,b){if(i.postResults==null)throw new Error('profiler has not been turned on');return i.postResults(a,b)};j.resetProfileResults=function(){if(i.resetResults==null)throw new Error('profiler has not been turned on');return i.resetResults()};j.DEBUG=false;function s(){};l([s],Error);function c(a,b,c){this.F=a.length;this.K=a;this.L=b;this.I=c;this.H=null;this.P=null};l([c],Object);function o(){};l([o],Object);function e(){var a;var b;var c;this.G={};a=this.D='';b=this._=0;c=this.A=a.length;this.E=0;this.C=b;this.B=c};l([e],o);function v(a,b){a.D=b.D;a._=b._;a.A=b.A;a.E=b.E;a.C=b.C;a.B=b.B};function f(b,d,c,e){var a;if(b._>=b.A){return false}a=b.D.charCodeAt(b._);if(a>e||a<c){return false}a-=c;if((d[a>>>3]&1<<(a&7))===0){return false}b._++;return true};function m(b,d,c,e){var a;if(b._<=b.E){return false}a=b.D.charCodeAt(b._-1);if(a>e||a<c){return false}a-=c;if((d[a>>>3]&1<<(a&7))===0){return false}b._--;return true};function n(a,d,c,e){var b;if(a._>=a.A){return false}b=a.D.charCodeAt(a._);if(b>e||b<c){a._++;return true}b-=c;if((d[b>>>3]&1<<(b&7))===0){a._++;return true}return false};function k(a,b,d){var c;if(a.A-a._<b){return false}if(a.D.slice(c=a._,c+b)!==d){return false}a._+=b;return true};function d(a,b,d){var c;if(a._-a.E<b){return false}if(a.D.slice((c=a._)-b,c)!==d){return false}a._-=b;return true};function p(f,m,p){var b;var d;var e;var n;var g;var k;var l;var i;var h;var c;var a;var j;var o;b=0;d=p;e=f._;n=f.A;g=0;k=0;l=false;while(true){i=b+(d-b>>>1);h=0;c=g<k?g:k;a=m[i];for(j=c;j<a.F;j++){if(e+c===n){h=-1;break}h=f.D.charCodeAt(e+c)-a.K.charCodeAt(j);if(h!==0){break}c++}if(h<0){d=i;k=c}else{b=i;g=c}if(d-b<=1){if(b>0){break}if(d===b){break}if(l){break}l=true}}while(true){a=m[b];if(g>=a.F){f._=e+a.F|0;if(a.H==null){return a.I}o=a.H(a.P);f._=e+a.F|0;if(o){return a.I}}b=a.L;if(b<0){return 0}}return-1};function h(d,m,p){var b;var g;var e;var n;var f;var k;var l;var i;var h;var c;var a;var j;var o;b=0;g=p;e=d._;n=d.E;f=0;k=0;l=false;while(true){i=b+(g-b>>1);h=0;c=f<k?f:k;a=m[i];for(j=a.F-1-c;j>=0;j--){if(e-c===n){h=-1;break}h=d.D.charCodeAt(e-1-c)-a.K.charCodeAt(j);if(h!==0){break}c++}if(h<0){g=i;k=c}else{b=i;f=c}if(g-b<=1){if(b>0){break}if(g===b){break}if(l){break}l=true}}while(true){a=m[b];if(f>=a.F){d._=e-a.F|0;if(a.H==null){return a.I}o=a.H(d);d._=e-a.F|0;if(o){return a.I}}b=a.L;if(b<0){return 0}}return-1};function D(a,b,d,e){var c;c=e.length-(d-b);a.D=a.D.slice(0,b)+e+a.D.slice(d);a.A+=c|0;if(a._>=d){a._+=c|0}else if(a._>b){a._=b}return c|0};function b(a,f){var b;var c;var d;var e;b=false;if((c=a.C)<0||c>(d=a.B)||d>(e=a.A)||e>a.D.length?false:true){D(a,a.C,a.B,f);b=true}return b};e.prototype.J=function(){return false};e.prototype.W=function(b){var a;var c;var d;var e;a=this.G['.'+b];if(a==null){c=this.D=b;d=this._=0;e=this.A=c.length;this.E=0;this.C=d;this.B=e;this.J();a=this.D;this.G['.'+b]=a}return a};e.prototype.stemWord=e.prototype.W;e.prototype.X=function(e){var d;var b;var c;var a;var f;var g;var h;d=[];for(b=0;b<e.length;b++){c=e[b];a=this.G['.'+c];if(a==null){f=this.D=c;g=this._=0;h=this.A=f.length;this.E=0;this.C=g;this.B=h;this.J();a=this.D;this.G['.'+c]=a}d.push(a)}return d};e.prototype.stemWords=e.prototype.X;function a(){e.call(this);this.I_x=0;this.I_p2=0;this.I_p1=0};l([a],e);a.prototype.M=function(a){this.I_x=a.I_x;this.I_p2=a.I_p2;this.I_p1=a.I_p1;v(this,a)};a.prototype.copy_from=a.prototype.M;a.prototype.U=function(){var m;var r;var n;var o;var d;var q;var e;var c;var g;var h;var i;var j;var l;var s;var p;m=this._;a:while(true){r=this._;e=true;b:while(e===true){e=false;c=true;c:while(c===true){c=false;n=this._;g=true;d:while(g===true){g=false;this.C=this._;if(!k(this,1,'ß')){break d}this.B=this._;if(!b(this,'ss')){return false}break c}s=this._=n;if(s>=this.A){break b}this._++}continue a}this._=r;break a}this._=m;b:while(true){o=this._;h=true;d:while(h===true){h=false;e:while(true){d=this._;i=true;a:while(i===true){i=false;if(!f(this,a.g_v,97,252)){break a}this.C=this._;j=true;f:while(j===true){j=false;q=this._;l=true;c:while(l===true){l=false;if(!k(this,1,'u')){break c}this.B=this._;if(!f(this,a.g_v,97,252)){break c}if(!b(this,'U')){return false}break f}this._=q;if(!k(this,1,'y')){break a}this.B=this._;if(!f(this,a.g_v,97,252)){break a}if(!b(this,'Y')){return false}}this._=d;break e}p=this._=d;if(p>=this.A){break d}this._++}continue b}this._=o;break b}return true};a.prototype.r_prelude=a.prototype.U;function G(c){var s;var n;var o;var p;var e;var r;var d;var g;var h;var i;var j;var l;var m;var t;var q;s=c._;a:while(true){n=c._;d=true;b:while(d===true){d=false;g=true;c:while(g===true){g=false;o=c._;h=true;d:while(h===true){h=false;c.C=c._;if(!k(c,1,'ß')){break d}c.B=c._;if(!b(c,'ss')){return false}break c}t=c._=o;if(t>=c.A){break b}c._++}continue a}c._=n;break a}c._=s;b:while(true){p=c._;i=true;d:while(i===true){i=false;e:while(true){e=c._;j=true;a:while(j===true){j=false;if(!f(c,a.g_v,97,252)){break a}c.C=c._;l=true;f:while(l===true){l=false;r=c._;m=true;c:while(m===true){m=false;if(!k(c,1,'u')){break c}c.B=c._;if(!f(c,a.g_v,97,252)){break c}if(!b(c,'U')){return false}break f}c._=r;if(!k(c,1,'y')){break a}c.B=c._;if(!f(c,a.g_v,97,252)){break a}if(!b(c,'Y')){return false}}c._=e;break e}q=c._=e;if(q>=c.A){break d}c._++}continue b}c._=p;break b}return true};a.prototype.S=function(){var j;var b;var d;var e;var c;var g;var h;var i;var l;var k;this.I_p1=i=this.A;this.I_p2=i;j=l=this._;b=l+3|0;if(0>b||b>i){return false}k=this._=b;this.I_x=k;this._=j;a:while(true){d=true;b:while(d===true){d=false;if(!f(this,a.g_v,97,252)){break b}break a}if(this._>=this.A){return false}this._++}a:while(true){e=true;b:while(e===true){e=false;if(!n(this,a.g_v,97,252)){break b}break a}if(this._>=this.A){return false}this._++}this.I_p1=this._;c=true;a:while(c===true){c=false;if(!(this.I_p1<this.I_x)){break a}this.I_p1=this.I_x}a:while(true){g=true;b:while(g===true){g=false;if(!f(this,a.g_v,97,252)){break b}break a}if(this._>=this.A){return false}this._++}a:while(true){h=true;b:while(h===true){h=false;if(!n(this,a.g_v,97,252)){break b}break a}if(this._>=this.A){return false}this._++}this.I_p2=this._;return true};a.prototype.r_mark_regions=a.prototype.S;function F(b){var k;var c;var e;var g;var d;var h;var i;var j;var m;var l;b.I_p1=j=b.A;b.I_p2=j;k=m=b._;c=m+3|0;if(0>c||c>j){return false}l=b._=c;b.I_x=l;b._=k;a:while(true){e=true;b:while(e===true){e=false;if(!f(b,a.g_v,97,252)){break b}break a}if(b._>=b.A){return false}b._++}a:while(true){g=true;b:while(g===true){g=false;if(!n(b,a.g_v,97,252)){break b}break a}if(b._>=b.A){return false}b._++}b.I_p1=b._;d=true;a:while(d===true){d=false;if(!(b.I_p1<b.I_x)){break a}b.I_p1=b.I_x}a:while(true){h=true;b:while(h===true){h=false;if(!f(b,a.g_v,97,252)){break b}break a}if(b._>=b.A){return false}b._++}a:while(true){i=true;b:while(i===true){i=false;if(!n(b,a.g_v,97,252)){break b}break a}if(b._>=b.A){return false}b._++}b.I_p2=b._;return true};a.prototype.T=function(){var c;var e;var d;b:while(true){e=this._;d=true;a:while(d===true){d=false;this.C=this._;c=p(this,a.a_0,6);if(c===0){break a}this.B=this._;switch(c){case 0:break a;case 1:if(!b(this,'y')){return false}break;case 2:if(!b(this,'u')){return false}break;case 3:if(!b(this,'a')){return false}break;case 4:if(!b(this,'o')){return false}break;case 5:if(!b(this,'u')){return false}break;case 6:if(this._>=this.A){break a}this._++;break}continue b}this._=e;break b}return true};a.prototype.r_postlude=a.prototype.T;function E(c){var d;var f;var e;b:while(true){f=c._;e=true;a:while(e===true){e=false;c.C=c._;d=p(c,a.a_0,6);if(d===0){break a}c.B=c._;switch(d){case 0:break a;case 1:if(!b(c,'y')){return false}break;case 2:if(!b(c,'u')){return false}break;case 3:if(!b(c,'a')){return false}break;case 4:if(!b(c,'o')){return false}break;case 5:if(!b(c,'u')){return false}break;case 6:if(c._>=c.A){break a}c._++;break}continue b}c._=f;break b}return true};a.prototype.Q=function(){return!(this.I_p1<=this._)?false:true};a.prototype.r_R1=a.prototype.Q;a.prototype.R=function(){return!(this.I_p2<=this._)?false:true};a.prototype.r_R2=a.prototype.R;a.prototype.V=function(){var c;var z;var n;var x;var y;var f;var A;var B;var p;var w;var g;var j;var k;var l;var e;var o;var i;var q;var r;var s;var t;var u;var v;var D;var E;var F;var G;var H;var I;var J;var K;var L;var M;var C;z=this.A-this._;j=true;a:while(j===true){j=false;this.B=this._;c=h(this,a.a_1,7);if(c===0){break a}this.C=D=this._;if(!(!(this.I_p1<=D)?false:true)){break a}switch(c){case 0:break a;case 1:if(!b(this,'')){return false}break;case 2:if(!b(this,'')){return false}n=this.A-this._;k=true;b:while(k===true){k=false;this.B=this._;if(!d(this,1,'s')){this._=this.A-n;break b}this.C=this._;if(!d(this,3,'nis')){this._=this.A-n;break b}if(!b(this,'')){return false}}break;case 3:if(!m(this,a.g_s_ending,98,116)){break a}if(!b(this,'')){return false}break}}G=this._=(F=this.A)-z;x=F-G;l=true;a:while(l===true){l=false;this.B=this._;c=h(this,a.a_2,4);if(c===0){break a}this.C=E=this._;if(!(!(this.I_p1<=E)?false:true)){break a}switch(c){case 0:break a;case 1:if(!b(this,'')){return false}break;case 2:if(!m(this,a.g_st_ending,98,116)){break a}e=this._-3|0;if(this.E>e||e>this.A){break a}this._=e;if(!b(this,'')){return false}break}}C=this._=(M=this.A)-x;y=M-C;o=true;a:while(o===true){o=false;this.B=this._;c=h(this,a.a_4,8);if(c===0){break a}this.C=H=this._;if(!(!(this.I_p2<=H)?false:true)){break a}switch(c){case 0:break a;case 1:if(!b(this,'')){return false}f=this.A-this._;i=true;b:while(i===true){i=false;this.B=this._;if(!d(this,2,'ig')){this._=this.A-f;break b}this.C=I=this._;A=this.A-I;q=true;c:while(q===true){q=false;if(!d(this,1,'e')){break c}this._=this.A-f;break b}J=this._=this.A-A;if(!(!(this.I_p2<=J)?false:true)){this._=this.A-f;break b}if(!b(this,'')){return false}}break;case 2:B=this.A-this._;r=true;b:while(r===true){r=false;if(!d(this,1,'e')){break b}break a}this._=this.A-B;if(!b(this,'')){return false}break;case 3:if(!b(this,'')){return false}p=this.A-this._;s=true;b:while(s===true){s=false;this.B=this._;t=true;c:while(t===true){t=false;w=this.A-this._;u=true;d:while(u===true){u=false;if(!d(this,2,'er')){break d}break c}this._=this.A-w;if(!d(this,2,'en')){this._=this.A-p;break b}}this.C=K=this._;if(!(!(this.I_p1<=K)?false:true)){this._=this.A-p;break b}if(!b(this,'')){return false}}break;case 4:if(!b(this,'')){return false}g=this.A-this._;v=true;b:while(v===true){v=false;this.B=this._;c=h(this,a.a_3,2);if(c===0){this._=this.A-g;break b}this.C=L=this._;if(!(!(this.I_p2<=L)?false:true)){this._=this.A-g;break b}switch(c){case 0:this._=this.A-g;break b;case 1:if(!b(this,'')){return false}break}}break}}this._=this.A-y;return true};a.prototype.r_standard_suffix=a.prototype.V;function A(c){var e;var A;var j;var y;var z;var g;var B;var C;var q;var x;var i;var k;var l;var n;var f;var p;var o;var r;var s;var t;var u;var v;var w;var E;var F;var G;var H;var I;var J;var K;var L;var M;var N;var D;A=c.A-c._;k=true;a:while(k===true){k=false;c.B=c._;e=h(c,a.a_1,7);if(e===0){break a}c.C=E=c._;if(!(!(c.I_p1<=E)?false:true)){break a}switch(e){case 0:break a;case 1:if(!b(c,'')){return false}break;case 2:if(!b(c,'')){return false}j=c.A-c._;l=true;b:while(l===true){l=false;c.B=c._;if(!d(c,1,'s')){c._=c.A-j;break b}c.C=c._;if(!d(c,3,'nis')){c._=c.A-j;break b}if(!b(c,'')){return false}}break;case 3:if(!m(c,a.g_s_ending,98,116)){break a}if(!b(c,'')){return false}break}}H=c._=(G=c.A)-A;y=G-H;n=true;a:while(n===true){n=false;c.B=c._;e=h(c,a.a_2,4);if(e===0){break a}c.C=F=c._;if(!(!(c.I_p1<=F)?false:true)){break a}switch(e){case 0:break a;case 1:if(!b(c,'')){return false}break;case 2:if(!m(c,a.g_st_ending,98,116)){break a}f=c._-3|0;if(c.E>f||f>c.A){break a}c._=f;if(!b(c,'')){return false}break}}D=c._=(N=c.A)-y;z=N-D;p=true;a:while(p===true){p=false;c.B=c._;e=h(c,a.a_4,8);if(e===0){break a}c.C=I=c._;if(!(!(c.I_p2<=I)?false:true)){break a}switch(e){case 0:break a;case 1:if(!b(c,'')){return false}g=c.A-c._;o=true;b:while(o===true){o=false;c.B=c._;if(!d(c,2,'ig')){c._=c.A-g;break b}c.C=J=c._;B=c.A-J;r=true;c:while(r===true){r=false;if(!d(c,1,'e')){break c}c._=c.A-g;break b}K=c._=c.A-B;if(!(!(c.I_p2<=K)?false:true)){c._=c.A-g;break b}if(!b(c,'')){return false}}break;case 2:C=c.A-c._;s=true;b:while(s===true){s=false;if(!d(c,1,'e')){break b}break a}c._=c.A-C;if(!b(c,'')){return false}break;case 3:if(!b(c,'')){return false}q=c.A-c._;t=true;b:while(t===true){t=false;c.B=c._;u=true;c:while(u===true){u=false;x=c.A-c._;v=true;d:while(v===true){v=false;if(!d(c,2,'er')){break d}break c}c._=c.A-x;if(!d(c,2,'en')){c._=c.A-q;break b}}c.C=L=c._;if(!(!(c.I_p1<=L)?false:true)){c._=c.A-q;break b}if(!b(c,'')){return false}}break;case 4:if(!b(c,'')){return false}i=c.A-c._;w=true;b:while(w===true){w=false;c.B=c._;e=h(c,a.a_3,2);if(e===0){c._=c.A-i;break b}c.C=M=c._;if(!(!(c.I_p2<=M)?false:true)){c._=c.A-i;break b}switch(e){case 0:c._=c.A-i;break b;case 1:if(!b(c,'')){return false}break}}break}}c._=c.A-z;return true};a.prototype.J=function(){var f;var g;var h;var b;var a;var c;var d;var i;var j;var e;f=this._;b=true;a:while(b===true){b=false;if(!G(this)){break a}}i=this._=f;g=i;a=true;a:while(a===true){a=false;if(!F(this)){break a}}j=this._=g;this.E=j;this._=this.A;c=true;a:while(c===true){c=false;if(!A(this)){break a}}e=this._=this.E;h=e;d=true;a:while(d===true){d=false;if(!E(this)){break a}}this._=h;return true};a.prototype.stem=a.prototype.J;a.prototype.N=function(b){return b instanceof a};a.prototype.equals=a.prototype.N;a.prototype.O=function(){var c;var a;var b;var d;c='GermanStemmer';a=0;for(b=0;b<c.length;b++){d=c.charCodeAt(b);a=(a<<5)-a+d;a=a&a}return a|0};a.prototype.hashCode=a.prototype.O;a.serialVersionUID=1;g(a,'methodObject',function(){return new a});g(a,'a_0',function(){return[new c('',-1,6),new c('U',0,2),new c('Y',0,1),new c('ä',0,3),new c('ö',0,4),new c('ü',0,5)]});g(a,'a_1',function(){return[new c('e',-1,2),new c('em',-1,1),new c('en',-1,2),new c('ern',-1,1),new c('er',-1,1),new c('s',-1,3),new c('es',5,2)]});g(a,'a_2',function(){return[new c('en',-1,1),new c('er',-1,1),new c('st',-1,2),new c('est',2,1)]});g(a,'a_3',function(){return[new c('ig',-1,1),new c('lich',-1,1)]});g(a,'a_4',function(){return[new c('end',-1,1),new c('ig',-1,2),new c('ung',-1,1),new c('lich',-1,3),new c('isch',-1,2),new c('ik',-1,2),new c('heit',-1,3),new c('keit',-1,4)]});g(a,'g_v',function(){return[17,65,16,1,0,0,0,0,0,0,0,0,0,0,0,0,8,0,32,8]});g(a,'g_s_ending',function(){return[117,30,5]});g(a,'g_st_ending',function(){return[117,30,4]});var q={'src/stemmer.jsx':{Stemmer:o},'src/german-stemmer.jsx':{GermanStemmer:a}}}(JSX))
var Stemmer = JSX.require("src/german-stemmer.jsx").GermanStemmer;



/**
 * Simple result scoring code.
 */
var Scorer = {
  // Implement the following function to further tweak the score for each result
  // The function takes a result array [filename, title, anchor, descr, score]
  // and returns the new score.
  /*
  score: function(result) {
    return result[4];
  },
  */

  // query matches the full name of an object
  objNameMatch: 11,
  // or matches in the last dotted part of the object name
  objPartialMatch: 6,
  // Additive scores depending on the priority of the object
  objPrio: {0:  15,   // used to be importantResults
            1:  5,   // used to be objectResults
            2: -5},  // used to be unimportantResults
  //  Used when the priority is not in the mapping.
  objPrioDefault: 0,

  // query found in title
  title: 15,
  // query found in terms
  term: 5
};





var splitChars = (function() {
    var result = {};
    var singles = [96, 180, 187, 191, 215, 247, 749, 885, 903, 907, 909, 930, 1014, 1648,
         1748, 1809, 2416, 2473, 2481, 2526, 2601, 2609, 2612, 2615, 2653, 2702,
         2706, 2729, 2737, 2740, 2857, 2865, 2868, 2910, 2928, 2948, 2961, 2971,
         2973, 3085, 3089, 3113, 3124, 3213, 3217, 3241, 3252, 3295, 3341, 3345,
         3369, 3506, 3516, 3633, 3715, 3721, 3736, 3744, 3748, 3750, 3756, 3761,
         3781, 3912, 4239, 4347, 4681, 4695, 4697, 4745, 4785, 4799, 4801, 4823,
         4881, 5760, 5901, 5997, 6313, 7405, 8024, 8026, 8028, 8030, 8117, 8125,
         8133, 8181, 8468, 8485, 8487, 8489, 8494, 8527, 11311, 11359, 11687, 11695,
         11703, 11711, 11719, 11727, 11735, 12448, 12539, 43010, 43014, 43019, 43587,
         43696, 43713, 64286, 64297, 64311, 64317, 64319, 64322, 64325, 65141];
    var i, j, start, end;
    for (i = 0; i < singles.length; i++) {
        result[singles[i]] = true;
    }
    var ranges = [[0, 47], [58, 64], [91, 94], [123, 169], [171, 177], [182, 184], [706, 709],
         [722, 735], [741, 747], [751, 879], [888, 889], [894, 901], [1154, 1161],
         [1318, 1328], [1367, 1368], [1370, 1376], [1416, 1487], [1515, 1519], [1523, 1568],
         [1611, 1631], [1642, 1645], [1750, 1764], [1767, 1773], [1789, 1790], [1792, 1807],
         [1840, 1868], [1958, 1968], [1970, 1983], [2027, 2035], [2038, 2041], [2043, 2047],
         [2070, 2073], [2075, 2083], [2085, 2087], [2089, 2307], [2362, 2364], [2366, 2383],
         [2385, 2391], [2402, 2405], [2419, 2424], [2432, 2436], [2445, 2446], [2449, 2450],
         [2483, 2485], [2490, 2492], [2494, 2509], [2511, 2523], [2530, 2533], [2546, 2547],
         [2554, 2564], [2571, 2574], [2577, 2578], [2618, 2648], [2655, 2661], [2672, 2673],
         [2677, 2692], [2746, 2748], [2750, 2767], [2769, 2783], [2786, 2789], [2800, 2820],
         [2829, 2830], [2833, 2834], [2874, 2876], [2878, 2907], [2914, 2917], [2930, 2946],
         [2955, 2957], [2966, 2968], [2976, 2978], [2981, 2983], [2987, 2989], [3002, 3023],
         [3025, 3045], [3059, 3076], [3130, 3132], [3134, 3159], [3162, 3167], [3170, 3173],
         [3184, 3191], [3199, 3204], [3258, 3260], [3262, 3293], [3298, 3301], [3312, 3332],
         [3386, 3388], [3390, 3423], [3426, 3429], [3446, 3449], [3456, 3460], [3479, 3481],
         [3518, 3519], [3527, 3584], [3636, 3647], [3655, 3663], [3674, 3712], [3717, 3718],
         [3723, 3724], [3726, 3731], [3752, 3753], [3764, 3772], [3774, 3775], [3783, 3791],
         [3802, 3803], [3806, 3839], [3841, 3871], [3892, 3903], [3949, 3975], [3980, 4095],
         [4139, 4158], [4170, 4175], [4182, 4185], [4190, 4192], [4194, 4196], [4199, 4205],
         [4209, 4212], [4226, 4237], [4250, 4255], [4294, 4303], [4349, 4351], [4686, 4687],
         [4702, 4703], [4750, 4751], [4790, 4791], [4806, 4807], [4886, 4887], [4955, 4968],
         [4989, 4991], [5008, 5023], [5109, 5120], [5741, 5742], [5787, 5791], [5867, 5869],
         [5873, 5887], [5906, 5919], [5938, 5951], [5970, 5983], [6001, 6015], [6068, 6102],
         [6104, 6107], [6109, 6111], [6122, 6127], [6138, 6159], [6170, 6175], [6264, 6271],
         [6315, 6319], [6390, 6399], [6429, 6469], [6510, 6511], [6517, 6527], [6572, 6592],
         [6600, 6607], [6619, 6655], [6679, 6687], [6741, 6783], [6794, 6799], [6810, 6822],
         [6824, 6916], [6964, 6980], [6988, 6991], [7002, 7042], [7073, 7085], [7098, 7167],
         [7204, 7231], [7242, 7244], [7294, 7400], [7410, 7423], [7616, 7679], [7958, 7959],
         [7966, 7967], [8006, 8007], [8014, 8015], [8062, 8063], [8127, 8129], [8141, 8143],
         [8148, 8149], [8156, 8159], [8173, 8177], [8189, 8303], [8306, 8307], [8314, 8318],
         [8330, 8335], [8341, 8449], [8451, 8454], [8456, 8457], [8470, 8472], [8478, 8483],
         [8506, 8507], [8512, 8516], [8522, 8525], [8586, 9311], [9372, 9449], [9472, 10101],
         [10132, 11263], [11493, 11498], [11503, 11516], [11518, 11519], [11558, 11567],
         [11622, 11630], [11632, 11647], [11671, 11679], [11743, 11822], [11824, 12292],
         [12296, 12320], [12330, 12336], [12342, 12343], [12349, 12352], [12439, 12444],
         [12544, 12548], [12590, 12592], [12687, 12689], [12694, 12703], [12728, 12783],
         [12800, 12831], [12842, 12880], [12896, 12927], [12938, 12976], [12992, 13311],
         [19894, 19967], [40908, 40959], [42125, 42191], [42238, 42239], [42509, 42511],
         [42540, 42559], [42592, 42593], [42607, 42622], [42648, 42655], [42736, 42774],
         [42784, 42785], [42889, 42890], [42893, 43002], [43043, 43055], [43062, 43071],
         [43124, 43137], [43188, 43215], [43226, 43249], [43256, 43258], [43260, 43263],
         [43302, 43311], [43335, 43359], [43389, 43395], [43443, 43470], [43482, 43519],
         [43561, 43583], [43596, 43599], [43610, 43615], [43639, 43641], [43643, 43647],
         [43698, 43700], [43703, 43704], [43710, 43711], [43715, 43738], [43742, 43967],
         [44003, 44015], [44026, 44031], [55204, 55215], [55239, 55242], [55292, 55295],
         [57344, 63743], [64046, 64047], [64110, 64111], [64218, 64255], [64263, 64274],
         [64280, 64284], [64434, 64466], [64830, 64847], [64912, 64913], [64968, 65007],
         [65020, 65135], [65277, 65295], [65306, 65312], [65339, 65344], [65371, 65381],
         [65471, 65473], [65480, 65481], [65488, 65489], [65496, 65497]];
    for (i = 0; i < ranges.length; i++) {
        start = ranges[i][0];
        end = ranges[i][1];
        for (j = start; j <= end; j++) {
            result[j] = true;
        }
    }
    return result;
})();

function splitQuery(query) {
    var result = [];
    var start = -1;
    for (var i = 0; i < query.length; i++) {
        if (splitChars[query.charCodeAt(i)]) {
            if (start !== -1) {
                result.push(query.slice(start, i));
                start = -1;
            }
        } else if (start === -1) {
            start = i;
        }
    }
    if (start !== -1) {
        result.push(query.slice(start));
    }
    return result;
}




/**
 * Search Module
 */
var Search = {

  _index : null,
  _queued_query : null,
  _pulse_status : -1,

  init : function() {
      var params = $.getQueryParameters();
      if (params.q) {
          var query = params.q[0];
          $('input[name="q"]')[0].value = query;
          this.performSearch(query);
      }
  },

  loadIndex : function(url) {
    $.ajax({type: "GET", url: url, data: null,
            dataType: "script", cache: true,
            complete: function(jqxhr, textstatus) {
              if (textstatus != "success") {
                document.getElementById("searchindexloader").src = url;
              }
            }});
  },

  setIndex : function(index) {
    var q;
    this._index = index;
    if ((q = this._queued_query) !== null) {
      this._queued_query = null;
      Search.query(q);
    }
  },

  hasIndex : function() {
      return this._index !== null;
  },

  deferQuery : function(query) {
      this._queued_query = query;
  },

  stopPulse : function() {
      this._pulse_status = 0;
  },

  startPulse : function() {
    if (this._pulse_status >= 0)
        return;
    function pulse() {
      var i;
      Search._pulse_status = (Search._pulse_status + 1) % 4;
      var dotString = '';
      for (i = 0; i < Search._pulse_status; i++)
        dotString += '.';
      Search.dots.text(dotString);
      if (Search._pulse_status > -1)
        window.setTimeout(pulse, 500);
    }
    pulse();
  },

  /**
   * perform a search for something (or wait until index is loaded)
   */
  performSearch : function(query) {
    // create the required interface elements
    this.out = $('#search-results');
    this.title = $('<h2>' + _('Searching') + '</h2>').appendTo(this.out);
    this.dots = $('<span></span>').appendTo(this.title);
    this.status = $('<p style="display: none"></p>').appendTo(this.out);
    this.output = $('<ul class="search"/>').appendTo(this.out);

    $('#search-progress').text(_('Preparing search...'));
    this.startPulse();

    // index already loaded, the browser was quick!
    if (this.hasIndex())
      this.query(query);
    else
      this.deferQuery(query);
  },

  /**
   * execute search (requires search index to be loaded)
   */
  query : function(query) {
    var i;
    var stopwords = ["aber","alle","allem","allen","aller","alles","als","also","am","an","ander","andere","anderem","anderen","anderer","anderes","anderm","andern","anderr","anders","auch","auf","aus","bei","bin","bis","bist","da","damit","dann","das","dasselbe","dazu","da\u00df","dein","deine","deinem","deinen","deiner","deines","dem","demselben","den","denn","denselben","der","derer","derselbe","derselben","des","desselben","dessen","dich","die","dies","diese","dieselbe","dieselben","diesem","diesen","dieser","dieses","dir","doch","dort","du","durch","ein","eine","einem","einen","einer","eines","einig","einige","einigem","einigen","einiger","einiges","einmal","er","es","etwas","euch","euer","eure","eurem","euren","eurer","eures","f\u00fcr","gegen","gewesen","hab","habe","haben","hat","hatte","hatten","hier","hin","hinter","ich","ihm","ihn","ihnen","ihr","ihre","ihrem","ihren","ihrer","ihres","im","in","indem","ins","ist","jede","jedem","jeden","jeder","jedes","jene","jenem","jenen","jener","jenes","jetzt","kann","kein","keine","keinem","keinen","keiner","keines","k\u00f6nnen","k\u00f6nnte","machen","man","manche","manchem","manchen","mancher","manches","mein","meine","meinem","meinen","meiner","meines","mich","mir","mit","muss","musste","nach","nicht","nichts","noch","nun","nur","ob","oder","ohne","sehr","sein","seine","seinem","seinen","seiner","seines","selbst","sich","sie","sind","so","solche","solchem","solchen","solcher","solches","soll","sollte","sondern","sonst","um","und","uns","unse","unsem","unsen","unser","unses","unter","viel","vom","von","vor","war","waren","warst","was","weg","weil","weiter","welche","welchem","welchen","welcher","welches","wenn","werde","werden","wie","wieder","will","wir","wird","wirst","wo","wollen","wollte","w\u00e4hrend","w\u00fcrde","w\u00fcrden","zu","zum","zur","zwar","zwischen","\u00fcber"];

    // stem the searchterms and add them to the correct list
    var stemmer = new Stemmer();
    var searchterms = [];
    var excluded = [];
    var hlterms = [];
    var tmp = splitQuery(query);
    var objectterms = [];
    for (i = 0; i < tmp.length; i++) {
      if (tmp[i] !== "") {
          objectterms.push(tmp[i].toLowerCase());
      }

      if ($u.indexOf(stopwords, tmp[i].toLowerCase()) != -1 || tmp[i].match(/^\d+$/) ||
          tmp[i] === "") {
        // skip this "word"
        continue;
      }
      // stem the word
      var word = stemmer.stemWord(tmp[i].toLowerCase());
      // prevent stemmer from cutting word smaller than two chars
      if(word.length < 3 && tmp[i].length >= 3) {
        word = tmp[i];
      }
      var toAppend;
      // select the correct list
      if (word[0] == '-') {
        toAppend = excluded;
        word = word.substr(1);
      }
      else {
        toAppend = searchterms;
        hlterms.push(tmp[i].toLowerCase());
      }
      // only add if not already in the list
      if (!$u.contains(toAppend, word))
        toAppend.push(word);
    }
    var highlightstring = '?highlight=' + $.urlencode(hlterms.join(" "));

    // console.debug('SEARCH: searching for:');
    // console.info('required: ', searchterms);
    // console.info('excluded: ', excluded);

    // prepare search
    var terms = this._index.terms;
    var titleterms = this._index.titleterms;

    // array of [filename, title, anchor, descr, score]
    var results = [];
    $('#search-progress').empty();

    // lookup as object
    for (i = 0; i < objectterms.length; i++) {
      var others = [].concat(objectterms.slice(0, i),
                             objectterms.slice(i+1, objectterms.length));
      results = results.concat(this.performObjectSearch(objectterms[i], others));
    }

    // lookup as search terms in fulltext
    results = results.concat(this.performTermsSearch(searchterms, excluded, terms, titleterms));

    // let the scorer override scores with a custom scoring function
    if (Scorer.score) {
      for (i = 0; i < results.length; i++)
        results[i][4] = Scorer.score(results[i]);
    }

    // now sort the results by score (in opposite order of appearance, since the
    // display function below uses pop() to retrieve items) and then
    // alphabetically
    results.sort(function(a, b) {
      var left = a[4];
      var right = b[4];
      if (left > right) {
        return 1;
      } else if (left < right) {
        return -1;
      } else {
        // same score: sort alphabetically
        left = a[1].toLowerCase();
        right = b[1].toLowerCase();
        return (left > right) ? -1 : ((left < right) ? 1 : 0);
      }
    });

    // for debugging
    //Search.lastresults = results.slice();  // a copy
    //console.info('search results:', Search.lastresults);

    // print the results
    var resultCount = results.length;
    function displayNextItem() {
      // results left, load the summary and display it
      if (results.length) {
        var item = results.pop();
        var listItem = $('<li style="display:none"></li>');
        if (DOCUMENTATION_OPTIONS.FILE_SUFFIX === '') {
          // dirhtml builder
          var dirname = item[0] + '/';
          if (dirname.match(/\/index\/$/)) {
            dirname = dirname.substring(0, dirname.length-6);
          } else if (dirname == 'index/') {
            dirname = '';
          }
          listItem.append($('<a/>').attr('href',
            DOCUMENTATION_OPTIONS.URL_ROOT + dirname +
            highlightstring + item[2]).html(item[1]));
        } else {
          // normal html builders
          listItem.append($('<a/>').attr('href',
            item[0] + DOCUMENTATION_OPTIONS.FILE_SUFFIX +
            highlightstring + item[2]).html(item[1]));
        }
        if (item[3]) {
          listItem.append($('<span> (' + item[3] + ')</span>'));
          Search.output.append(listItem);
          listItem.slideDown(5, function() {
            displayNextItem();
          });
        } else if (DOCUMENTATION_OPTIONS.HAS_SOURCE) {
          var suffix = DOCUMENTATION_OPTIONS.SOURCELINK_SUFFIX;
          if (suffix === undefined) {
            suffix = '.txt';
          }
          $.ajax({url: DOCUMENTATION_OPTIONS.URL_ROOT + '_sources/' + item[5] + (item[5].slice(-suffix.length) === suffix ? '' : suffix),
                  dataType: "text",
                  complete: function(jqxhr, textstatus) {
                    var data = jqxhr.responseText;
                    if (data !== '' && data !== undefined) {
                      listItem.append(Search.makeSearchSummary(data, searchterms, hlterms));
                    }
                    Search.output.append(listItem);
                    listItem.slideDown(5, function() {
                      displayNextItem();
                    });
                  }});
        } else {
          // no source available, just display title
          Search.output.append(listItem);
          listItem.slideDown(5, function() {
            displayNextItem();
          });
        }
      }
      // search finished, update title and status message
      else {
        Search.stopPulse();
        Search.title.text(_('Search Results'));
        if (!resultCount)
          Search.status.text(_('Your search did not match any documents. Please make sure that all words are spelled correctly and that you\'ve selected enough categories.'));
        else
            Search.status.text(_('Search finished, found %s page(s) matching the search query.').replace('%s', resultCount));
        Search.status.fadeIn(500);
      }
    }
    displayNextItem();
  },

  /**
   * search for object names
   */
  performObjectSearch : function(object, otherterms) {
    var filenames = this._index.filenames;
    var docnames = this._index.docnames;
    var objects = this._index.objects;
    var objnames = this._index.objnames;
    var titles = this._index.titles;

    var i;
    var results = [];

    for (var prefix in objects) {
      for (var name in objects[prefix]) {
        var fullname = (prefix ? prefix + '.' : '') + name;
        if (fullname.toLowerCase().indexOf(object) > -1) {
          var score = 0;
          var parts = fullname.split('.');
          // check for different match types: exact matches of full name or
          // "last name" (i.e. last dotted part)
          if (fullname == object || parts[parts.length - 1] == object) {
            score += Scorer.objNameMatch;
          // matches in last name
          } else if (parts[parts.length - 1].indexOf(object) > -1) {
            score += Scorer.objPartialMatch;
          }
          var match = objects[prefix][name];
          var objname = objnames[match[1]][2];
          var title = titles[match[0]];
          // If more than one term searched for, we require other words to be
          // found in the name/title/description
          if (otherterms.length > 0) {
            var haystack = (prefix + ' ' + name + ' ' +
                            objname + ' ' + title).toLowerCase();
            var allfound = true;
            for (i = 0; i < otherterms.length; i++) {
              if (haystack.indexOf(otherterms[i]) == -1) {
                allfound = false;
                break;
              }
            }
            if (!allfound) {
              continue;
            }
          }
          var descr = objname + _(', in ') + title;

          var anchor = match[3];
          if (anchor === '')
            anchor = fullname;
          else if (anchor == '-')
            anchor = objnames[match[1]][1] + '-' + fullname;
          // add custom score for some objects according to scorer
          if (Scorer.objPrio.hasOwnProperty(match[2])) {
            score += Scorer.objPrio[match[2]];
          } else {
            score += Scorer.objPrioDefault;
          }
          results.push([docnames[match[0]], fullname, '#'+anchor, descr, score, filenames[match[0]]]);
        }
      }
    }

    return results;
  },

  /**
   * search for full-text terms in the index
   */
  performTermsSearch : function(searchterms, excluded, terms, titleterms) {
    var docnames = this._index.docnames;
    var filenames = this._index.filenames;
    var titles = this._index.titles;

    var i, j, file;
    var fileMap = {};
    var scoreMap = {};
    var results = [];

    // perform the search on the required terms
    for (i = 0; i < searchterms.length; i++) {
      var word = searchterms[i];
      var files = [];
      var _o = [
        {files: terms[word], score: Scorer.term},
        {files: titleterms[word], score: Scorer.title}
      ];

      // no match but word was a required one
      if ($u.every(_o, function(o){return o.files === undefined;})) {
        break;
      }
      // found search word in contents
      $u.each(_o, function(o) {
        var _files = o.files;
        if (_files === undefined)
          return

        if (_files.length === undefined)
          _files = [_files];
        files = files.concat(_files);

        // set score for the word in each file to Scorer.term
        for (j = 0; j < _files.length; j++) {
          file = _files[j];
          if (!(file in scoreMap))
            scoreMap[file] = {}
          scoreMap[file][word] = o.score;
        }
      });

      // create the mapping
      for (j = 0; j < files.length; j++) {
        file = files[j];
        if (file in fileMap)
          fileMap[file].push(word);
        else
          fileMap[file] = [word];
      }
    }

    // now check if the files don't contain excluded terms
    for (file in fileMap) {
      var valid = true;

      // check if all requirements are matched
      if (fileMap[file].length != searchterms.length)
          continue;

      // ensure that none of the excluded terms is in the search result
      for (i = 0; i < excluded.length; i++) {
        if (terms[excluded[i]] == file ||
            titleterms[excluded[i]] == file ||
            $u.contains(terms[excluded[i]] || [], file) ||
            $u.contains(titleterms[excluded[i]] || [], file)) {
          valid = false;
          break;
        }
      }

      // if we have still a valid result we can add it to the result list
      if (valid) {
        // select one (max) score for the file.
        // for better ranking, we should calculate ranking by using words statistics like basic tf-idf...
        var score = $u.max($u.map(fileMap[file], function(w){return scoreMap[file][w]}));
        results.push([docnames[file], titles[file], '', null, score, filenames[file]]);
      }
    }
    return results;
  },

  /**
   * helper function to return a node containing the
   * search summary for a given text. keywords is a list
   * of stemmed words, hlwords is the list of normal, unstemmed
   * words. the first one is used to find the occurrence, the
   * latter for highlighting it.
   */
  makeSearchSummary : function(text, keywords, hlwords) {
    var textLower = text.toLowerCase();
    var start = 0;
    $.each(keywords, function() {
      var i = textLower.indexOf(this.toLowerCase());
      if (i > -1)
        start = i;
    });
    start = Math.max(start - 120, 0);
    var excerpt = ((start > 0) ? '...' : '') +
      $.trim(text.substr(start, 240)) +
      ((start + 240 - text.length) ? '...' : '');
    var rv = $('<div class="context"></div>').text(excerpt);
    $.each(hlwords, function() {
      rv = rv.highlightText(this, 'highlighted');
    });
    return rv;
  }
};

$(document).ready(function() {
  Search.init();
});