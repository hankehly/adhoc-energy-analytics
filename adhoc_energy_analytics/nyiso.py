import io
from zipfile import ZipFile

import gridstatus
import pandas as pd

from adhoc_energy_analytics.constants import get_default_download_dir


class NYISOWithLocalZip(gridstatus.NYISO):
    """
    Subclass NYISO to override the _download_nyiso_archive method to read from a local zip file
    because NYISO does not sanction downloading data from their website programmatically.

    The zipped files should be pre-downloaded from NYISO's website and placed in the specified download directory.

    Here is the link to the NYISO archives:
    https://mis.nyiso.com/public/P-2Alist.htm
    """

    # Override init to set the download directory
    def __init__(self, *args, download_dir=None, **kwargs):
        if download_dir is None:
            download_dir = get_default_download_dir()
        self.download_dir = download_dir
        super().__init__(*args, **kwargs)

    def _download_nyiso_archive(
        self,
        date: str | pd.Timestamp,
        end: str | pd.Timestamp | None = None,
        dataset_name: str | None = None,
        filename: str | None = None,
        groupby: str | None = None,
        verbose: bool = False,
    ):
        """
        Override to prevent downloading from NYISO's website.
        Instead, we will read from a pre-downloaded zip file.
        """
        if filename is None:
            filename = dataset_name

        # NB: need to add the file date to the load forecast dataset to get the
        # forecast publish time.
        add_file_date = gridstatus.nyiso.LOAD_FORECAST_DATASET == dataset_name

        date = gridstatus.utils._handle_date(date, self.default_timezone)
        month = date.strftime("%Y%m01")
        day = date.strftime("%Y%m%d")

        # NB: if requesting the same day then just download the single file
        if end is not None and date.normalize() == end.normalize():
            end = None
            date = date.normalize()

        # NB: the last 7 days of file are hosted directly as csv
        # todo this can probably be optimized to a single csv in
        # a range and all files are in the last 7 days
        if end is None and date > pd.Timestamp.now(
            tz=self.default_timezone,
        ).normalize() - pd.DateOffset(days=7):
            raise NotImplementedError()
        else:
            # Get files from download dir
            zip_url = self.download_dir / f"{month}{filename}_csv.zip"
            if verbose:
                print(f"Reading from {zip_url}")
            with open(zip_url, "rb") as f:
                z = ZipFile(io.BytesIO(f.read()))

            all_dfs = []
            if end is None:
                date_range = [date]
            else:
                date_range = pd.date_range(
                    date.date(),
                    end.date(),
                    freq="1D",
                    inclusive="left",
                ).tolist()

                # NB: this handles case where end is the first of the next month
                # this pops up from the support_date_range decorator
                # and that date will be handled in the next month's zip file
                if end.month == date.month:
                    date_range += [end]

            for d in date_range:
                d = gridstatus.utils._handle_date(d, tz=self.default_timezone)
                month = d.strftime("%Y%m01")
                day = d.strftime("%Y%m%d")

                csv_filename = f"{day}{filename}.csv"
                if csv_filename not in z.namelist():
                    print(f"{csv_filename} not found in {zip_url}")
                    continue
                df = pd.read_csv(z.open(csv_filename))

                if add_file_date:
                    # NB: The File Date is the last modified time of the individual csv file
                    df["File Date"] = pd.Timestamp(
                        *z.getinfo(csv_filename).date_time,
                        tz=self.default_timezone,
                    )
                df = self._handle_time(df, dataset_name, groupby=groupby)

                # The column 'Marginal Cost Congestion ($/MWH' might exist,
                # in which case we need to add an ending 'r)'
                if "Marginal Cost Congestion ($/MWH" in df.columns:
                    df.rename(
                        columns={
                            "Marginal Cost Congestion ($/MWH": "Marginal Cost Congestion ($/MWHr)"
                        },
                        inplace=True,
                    )

                all_dfs.append(df)
            df = pd.concat(all_dfs)
        return df.sort_values("Time").reset_index(drop=True)
