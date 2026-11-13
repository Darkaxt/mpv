/*
 * GPU-completed per-frame inference timing windows for vf_animejanai.
 *
 * This file is part of mpv.
 *
 * mpv is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or (at your option) any later version.
 *
 * mpv is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with mpv.  If not, see <http://www.gnu.org/licenses/>.
 */

#pragma once

#include <stdbool.h>
#include <stdlib.h>

// Samples per reported window. 240 frames is 10 s at 24 fps; the host
// benchmark (480 frames) therefore sees two complete windows.
#define AJN_TIMING_WINDOW 240

struct ajn_timing {
    float ms[AJN_TIMING_WINDOW];
    int n;
};

struct ajn_timing_summary {
    int frames;
    double mean_ms, p50_ms, p95_ms, max_ms;
};

static int ajn_timing_cmp(const void *a, const void *b)
{
    float x = *(const float *)a, y = *(const float *)b;
    return (x > y) - (x < y);
}

// Adds one sample. Returns true when the window is full and should be
// summarized. Negative or non-finite samples are ignored.
static inline bool ajn_timing_add(struct ajn_timing *t, float ms)
{
    if (!(ms >= 0.0f && ms < 1e6f))
        return false;
    if (t->n < AJN_TIMING_WINDOW)
        t->ms[t->n++] = ms;
    return t->n >= AJN_TIMING_WINDOW;
}

// Nearest-rank percentile of a sorted array of n > 0 samples.
static inline double ajn_timing_rank(const float *sorted, int n, double q)
{
    int k = (int)(q * n + 0.999999);   // ceil(q * n)
    if (k < 1)
        k = 1;
    if (k > n)
        k = n;
    return sorted[k - 1];
}

// Summarizes and empties the window. Returns false (summary untouched) when
// it holds fewer than min_frames samples; the samples are dropped either way.
static inline bool ajn_timing_take(struct ajn_timing *t, int min_frames,
                                   struct ajn_timing_summary *s)
{
    int n = t->n;
    t->n = 0;
    if (n < 1 || n < min_frames)
        return false;
    qsort(t->ms, n, sizeof(t->ms[0]), ajn_timing_cmp);
    double sum = 0;
    for (int i = 0; i < n; i++)
        sum += t->ms[i];
    s->frames = n;
    s->mean_ms = sum / n;
    s->p50_ms = ajn_timing_rank(t->ms, n, 0.50);
    s->p95_ms = ajn_timing_rank(t->ms, n, 0.95);
    s->max_ms = t->ms[n - 1];
    return true;
}
