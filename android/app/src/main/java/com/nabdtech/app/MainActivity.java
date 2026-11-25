package com.nabdtech.app;

import android.app.Activity;
import android.content.Intent;
import android.graphics.Color;
import android.net.ConnectivityManager;
import android.net.NetworkInfo;
import android.net.Uri;
import android.os.Bundle;
import android.view.Gravity;
import android.view.View;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.TextView;

public class MainActivity extends Activity {
    private static final String HOME = "https://ahmedgamal20000006-stack.github.io/ai-akhbar/";
    private WebView web;
    private LinearLayout offline;
    private FrameLayout root;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        root = new FrameLayout(this);
        root.setBackgroundColor(Color.rgb(11, 16, 32));

        web = new WebView(this);
        web.getSettings().setJavaScriptEnabled(true);
        web.getSettings().setDomStorageEnabled(true);
        web.getSettings().setDatabaseEnabled(true);
        web.setWebChromeClient(new WebChromeClient());
        web.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest req) {
                Uri u = req.getUrl();
                if (u.getHost() != null && u.getHost().endsWith("github.io")) return false;
                startActivity(new Intent(Intent.ACTION_VIEW, u));
                return true;
            }
            @Override
            public void onReceivedError(WebView view, int code, String desc, String url) {
                if (url != null && url.startsWith(HOME)) showOffline();
            }
        });
        root.addView(web, new FrameLayout.LayoutParams(-1, -1));

        offline = new LinearLayout(this);
        offline.setOrientation(LinearLayout.VERTICAL);
        offline.setGravity(Gravity.CENTER);
        offline.setBackgroundColor(Color.rgb(11, 16, 32));
        TextView t = new TextView(this);
        t.setText("مفيش اتصال بالنت\nافتح النت واضغط حاول تاني");
        t.setTextColor(Color.WHITE);
        t.setTextSize(18);
        t.setGravity(Gravity.CENTER);
        t.setPadding(40, 0, 40, 40);
        Button b = new Button(this);
        b.setText("حاول تاني");
        b.setOnClickListener(v -> load());
        offline.addView(t);
        offline.addView(b);
        offline.setVisibility(View.GONE);
        root.addView(offline, new FrameLayout.LayoutParams(-1, -1));

        setContentView(root);
        load();
    }

    private void load() {
        offline.setVisibility(View.GONE);
        web.setVisibility(View.VISIBLE);
        web.loadUrl(HOME);
    }

    private void showOffline() {
        web.setVisibility(View.GONE);
        offline.setVisibility(View.VISIBLE);
    }

    @Override
    protected void onResume() {
        super.onResume();
        ConnectivityManager cm = (ConnectivityManager) getSystemService(CONNECTIVITY_SERVICE);
        NetworkInfo ni = cm.getActiveNetworkInfo();
        if (ni != null && ni.isConnected() && web.getVisibility() == View.VISIBLE) {
            web.reload();
        }
    }

    @Override
    public void onBackPressed() {
        if (web.getVisibility() == View.VISIBLE && web.canGoBack()) web.goBack();
        else super.onBackPressed();
    }
}
