import streamlit as st
import pandas as pd
import os


def render_ai_subsystem():
    st.markdown("<h1>System Architecture: ML Models</h1>", unsafe_allow_html=True)
    st.markdown(
        "Remote endpoint integration to DagsHub MLFlow tracking server. Click below to establish a live connection to the ML server. This ensures the dashboard loads instantly while only retrieving heavy ML logs on demand."
    )

    # Using a button to prevent auto-loading which caused timeouts
    if st.button(
        "🔌 Establish Secure Connection to DagsHub MLFlow", use_container_width=True
    ):

        @st.cache_data(ttl=3600, show_spinner="Syncing remote experiments...")
        def fetch_dagshub_mlflow():
            import mlflow
            from mlflow.tracking import MlflowClient

            os.environ["MLFLOW_TRACKING_URI"] = (
                "https://dagshub.com/aletbm/S02-26-E45-Data_Science_EquineLead.mlflow"
            )
            mlflow.set_tracking_uri(os.environ["MLFLOW_TRACKING_URI"])
            client = MlflowClient()
            data = []
            try:
                experiments = client.search_experiments()
                for exp in experiments:
                    if exp.name == "Default":
                        continue
                    exp_data = {"name": exp.name, "runs": []}
                    if exp.name == "EquineLead_LeadScoring":
                        runs = client.search_runs(
                            experiment_ids=[exp.experiment_id],
                            filter_string="tags.`status` = 'champion'",
                            max_results=2,
                        )
                    else:
                        runs = client.search_runs(
                            experiment_ids=[exp.experiment_id],
                            order_by=["attribute.start_time DESC"],
                            max_results=2,
                        )

                    for r in runs:
                        run_info = {
                            "id": r.info.run_id,
                            "name": r.info.run_name,
                            "metrics": r.data.metrics,
                            "params": r.data.params,
                            "plots": [],
                        }
                        # Find plots
                        import tempfile

                        tmp = tempfile.mkdtemp()

                        def get_arts(path):
                            res = []
                            for i in client.list_artifacts(r.info.run_id, path):
                                if i.is_dir:
                                    res.extend(get_arts(i.path))
                                else:
                                    res.append(i.path)
                            return res

                        paths = get_arts("")
                        for p in paths:
                            if p.endswith(".png"):
                                dl_path = mlflow.artifacts.download_artifacts(
                                    run_id=r.info.run_id, artifact_path=p, dst_path=tmp
                                )
                                run_info["plots"].append(dl_path)
                        exp_data["runs"].append(run_info)
                    data.append(exp_data)
                return {"status": "success", "data": data}
            except Exception as e:
                return {"status": "error", "error": str(e)}

        res = fetch_dagshub_mlflow()
        if res["status"] == "error":
            st.error(f"Connection Failed: {res['error']}")
        else:
            st.success("✅ Secure Connection Established.")
            for exp in res["data"]:
                st.markdown(f"### 🧪 Experiment: `{exp['name']}`")
                for run in exp["runs"]:
                    with st.expander(
                        f"Run Execution: {run['name']} ({run['id']})", expanded=True
                    ):
                        c1, c2 = st.columns(2)
                        with c1:
                            st.write("**Evaluation Metrics**")
                            if run["metrics"]:
                                st.dataframe(
                                    pd.DataFrame(
                                        list(run["metrics"].items()),
                                        columns=["Metric", "Value"],
                                    ),
                                    use_container_width=True,
                                    hide_index=True,
                                )
                            else:
                                st.caption("No metrics")
                        with c2:
                            st.write("**Hyperparameters**")
                            if run["params"]:
                                st.dataframe(
                                    pd.DataFrame(
                                        list(run["params"].items()),
                                        columns=["Parameter", "Value"],
                                    ),
                                    use_container_width=True,
                                    hide_index=True,
                                )
                            else:
                                st.caption("No params")

                        st.markdown("---")
                        st.write("**Visual Artifacts**")
                        if run["plots"]:
                            p_cols = st.columns(min(len(run["plots"]), 3))
                            for idx, plot in enumerate(run["plots"]):
                                with p_cols[idx % 3]:
                                    st.image(plot, use_container_width=True)
                        else:
                            st.caption("No plot artifacts found.")
                st.markdown(
                    "<hr style='border: 1px solid #2D3748;'>", unsafe_allow_html=True
                )
