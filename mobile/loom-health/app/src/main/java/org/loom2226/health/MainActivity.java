package org.loom2226.health;

import android.app.Activity;
import android.os.Bundle;
import android.os.Build;
import android.content.Intent;
import android.net.Uri;
import android.graphics.Color;
import android.view.View;
import android.widget.*;
import org.json.*;
import java.net.*;
import java.io.*;

public class MainActivity extends Activity {
  LinearLayout root; TextView headline,detail,coverage; String runUrl="https://github.com/loom-2226/loom-2226/actions/workflows/loom-simulation-health.yml";
  TextView text(String value,int size,int color){TextView t=new TextView(this);t.setText(value);t.setTextSize(size);t.setTextColor(color);t.setPadding(0,12,0,12);root.addView(t);return t;}
  void open(String url){startActivity(new Intent(Intent.ACTION_VIEW,Uri.parse(url)));}
  @Override public void onCreate(Bundle b){super.onCreate(b);root=new LinearLayout(this);root.setOrientation(1);root.setPadding(32,44,32,20);root.setBackgroundColor(Color.rgb(15,19,27));root.setFitsSystemWindows(true);setContentView(root);
    text("LOOM  /  SIMULATION HEALTH",20,Color.WHITE);
    headline=text("Checking GitHub…",29,Color.WHITE);
    detail=text("",16,0xffd0d5dd);
    coverage=text("Coverage is determined by the GitHub workflow version, not the APK.",16,0xffffc46b);
    Button refresh=new Button(this);refresh.setText("REFRESH");root.addView(refresh);refresh.setOnClickListener(v->load());
    Button logs=new Button(this);logs.setText("OPEN GITHUB RUN");root.addView(logs);logs.setOnClickListener(v->open(runUrl));
    text("Source: public GitHub Actions • main branch • read-only",13,0xff9aa4b2);load();
  }
  void load(){headline.setText("Checking GitHub…");new Thread(()->{
    String status="UNAVAILABLE", info="Could not read GitHub Actions. Check connection or API limits.";String url=runUrl;int color=0xffffc46b;
    try {
      URL endpoint=new URL("https://api.github.com/repos/loom-2226/loom-2226/actions/workflows/loom-simulation-health.yml/runs?branch=main&per_page=1");
      HttpURLConnection conn=(HttpURLConnection)endpoint.openConnection();conn.setConnectTimeout(10000);conn.setReadTimeout(10000);conn.setRequestProperty("Accept","application/vnd.github+json");conn.setRequestProperty("User-Agent","LOOM-Health-Android");
      if(conn.getResponseCode()!=200)throw new IOException("GitHub API HTTP "+conn.getResponseCode());
      ByteArrayOutputStream bytes=new ByteArrayOutputStream();try(InputStream in=conn.getInputStream()){byte[] buf=new byte[4096];int n;while((n=in.read(buf))!=-1)bytes.write(buf,0,n);}
      JSONArray runs=new JSONObject(bytes.toString("UTF-8")).getJSONArray("workflow_runs");
      if(runs.length()==0){status="NO MAIN RUN";info="No workflow result on main yet.";}
      else {JSONObject r=runs.getJSONObject(0);String sha=r.optString("head_sha");String state=r.optString("status");String conclusion=r.optString("conclusion");url=r.optString("html_url",runUrl);
        if(!"completed".equals(state)){status="RUNNING";color=0xffffc46b;}
        else if("success".equals(conclusion)){status=r.optString("display_title").equals("LOOM Integrated Simulation Health")?"PASS • INTEGRATED":"PASS • PARTIAL";color=0xff72d99b;}
        else {status="FAIL • "+conclusion.toUpperCase();color=0xffff7979;}
        info="Commit: "+sha.substring(0,Math.min(10,sha.length()))+"\nRun: "+r.optString("run_number")+"\nUpdated: "+r.optString("updated_at")+"\nGitHub result: "+state+" / "+conclusion;
      }
    }catch(Exception e){info=info+"\n"+e.getMessage();}
    final String s=status,i=info,u=url;final int c=color;runOnUiThread(()->{headline.setText(s);headline.setTextColor(c);detail.setText(i);runUrl=u;});
  }).start();}
}
