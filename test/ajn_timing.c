/* SPDX-License-Identifier: LGPL-2.1-or-later */
#undef NDEBUG
#include <assert.h>
#include <math.h>
#include "video/filter/ajn_timing.h"

int main(void)
{
    struct ajn_timing t = {0};
    struct ajn_timing_summary s = {0};

    // window fills after exactly AJN_TIMING_WINDOW valid samples
    for (int i = 1; i < AJN_TIMING_WINDOW; i++)
        assert(!ajn_timing_add(&t, (float)(AJN_TIMING_WINDOW - i + 1)));
    assert(!ajn_timing_add(&t, -1.0f));        // ignored
    assert(!ajn_timing_add(&t, NAN));          // ignored
    assert(ajn_timing_add(&t, 1.0f));
    assert(t.n == AJN_TIMING_WINDOW);

    // samples 1..240 (inserted in descending order)
    assert(ajn_timing_take(&t, AJN_TIMING_WINDOW, &s));
    assert(t.n == 0);
    assert(s.frames == AJN_TIMING_WINDOW);
    assert(fabs(s.mean_ms - 120.5) < 1e-9);
    assert(s.p50_ms == 120.0);                 // nearest rank ceil(0.5*240)
    assert(s.p95_ms == 228.0);                 // ceil(0.95*240) = 228
    assert(s.max_ms == 240.0);

    // a partial window below the minimum is dropped
    for (int i = 0; i < 10; i++)
        ajn_timing_add(&t, 5.0f);
    s.frames = -1;
    assert(!ajn_timing_take(&t, 24, &s));
    assert(s.frames == -1 && t.n == 0);

    // a partial window at the minimum is reported; one slow outlier sets p95
    // only once it exceeds 5% of the samples
    for (int i = 0; i < 39; i++)
        ajn_timing_add(&t, 10.0f);
    ajn_timing_add(&t, 50.0f);
    assert(ajn_timing_take(&t, 24, &s));
    assert(s.frames == 40 && s.p95_ms == 10.0 && s.max_ms == 50.0);

    for (int i = 0; i < 37; i++)
        ajn_timing_add(&t, 10.0f);
    for (int i = 0; i < 3; i++)
        ajn_timing_add(&t, 50.0f);
    assert(ajn_timing_take(&t, 1, &s));
    assert(s.p95_ms == 50.0);

    assert(!ajn_timing_take(&t, 0, &s));       // empty never reports
    return 0;
}
