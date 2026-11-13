package @@PACKAGE@@;

import android.app.Activity;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;

/** 사이트 파일(assets/site)을 앱 안에서 그대로 보여 준다. 서버도 인터넷도 필요 없다. 바깥 주소는 휴대폰의 브라우저로 넘긴다. */
public class MainActivity extends Activity {
    private static final String HOST = "app.local";
    private WebView web;

    @Override
    protected void onCreate(Bundle b) {
        super.onCreate(b);
        web = new WebView(this);
        setContentView(web);
        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        web.setWebViewClient(new WebViewClient() {
            @Override
            public WebResourceResponse shouldInterceptRequest(WebView v, WebResourceRequest r) {
                Uri u = r.getUrl();
                if (!HOST.equals(u.getHost())) return null;
                String p = u.getPath();
                if (p == null || p.isEmpty()) p = "/";
                if (p.endsWith("/")) p = p + "index.html";
                InputStream in = open(p);
                if (in == null) in = open(p + "/index.html");
                if (in == null) {
                    return new WebResourceResponse("text/html", "utf-8", 404, "Not Found", null,
                            new ByteArrayInputStream("<meta charset=utf-8><p>없는 페이지입니다.</p>".getBytes()));
                }
                return new WebResourceResponse(mime(p), "utf-8", in);
            }

            @Override
            public boolean shouldOverrideUrlLoading(WebView v, WebResourceRequest r) {
                Uri u = r.getUrl();
                if (HOST.equals(u.getHost())) return false;
                startActivity(new Intent(Intent.ACTION_VIEW, u));
                return true;
            }
        });
        web.loadUrl("https://" + HOST + "/");
    }

    private InputStream open(String path) {
        try {
            return getAssets().open("site" + path);
        } catch (IOException e) {
            return null;
        }
    }

    private static String mime(String p) {
        String q = p.toLowerCase();
        if (q.endsWith(".html")) return "text/html";
        if (q.endsWith(".css")) return "text/css";
        if (q.endsWith(".js")) return "application/javascript";
        if (q.endsWith(".json") || q.endsWith(".webmanifest")) return "application/json";
        if (q.endsWith(".svg")) return "image/svg+xml";
        if (q.endsWith(".png")) return "image/png";
        if (q.endsWith(".jpg") || q.endsWith(".jpeg")) return "image/jpeg";
        if (q.endsWith(".webp")) return "image/webp";
        if (q.endsWith(".ico")) return "image/x-icon";
        if (q.endsWith(".xml")) return "application/xml";
        if (q.endsWith(".txt")) return "text/plain";
        if (q.endsWith(".woff2")) return "font/woff2";
        return "application/octet-stream";
    }

    @Override
    public void onBackPressed() {
        if (web.canGoBack()) web.goBack();
        else super.onBackPressed();
    }
}
