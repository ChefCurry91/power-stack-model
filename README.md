## Known limitations

* **Wind generation:** Wind generation still uses a single weather point as a proxy for all of Germany, although installed wind capacity is geographically distributed. A more accurate implementation would use multiple regional weather points and account for the geographical distribution of wind capacity.

* **Solar generation:** Solar generation is now geographically clustered, but the underlying dataset mainly covers ground-mounted installations. Cluster capacities are therefore scaled to the national ENTSO-E solar capacity to approximate the full German solar fleet. A more detailed representation would include the geographical distribution of rooftop PV.
