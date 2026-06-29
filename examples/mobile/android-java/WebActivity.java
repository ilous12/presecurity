package example;

import android.app.Activity;
import android.os.Bundle;
import android.webkit.WebView;

public class WebActivity extends Activity {
  @Override
  protected void onCreate(Bundle state) {
    super.onCreate(state);
    WebView webView = new WebView(this);
    webView.getSettings().setJavaScriptEnabled(true);
    webView.addJavascriptInterface(new NativeBridge(), "bridge");
    // Intentional fixture: external intent controls content loaded into WebView.
    webView.loadUrl(getIntent().getStringExtra("url"));
    setContentView(webView);
  }

  public static class NativeBridge {
    @android.webkit.JavascriptInterface
    public String token() {
      return "session-token";
    }
  }
}
