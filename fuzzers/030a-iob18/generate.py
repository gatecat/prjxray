#!/usr/bin/env python3

from prjxray.segmaker import Segmaker
from prjxray import segmaker
from prjxray import verilog
import os
import json


def bitfilter(frame, word):
    if frame < 38:
        return False

    return True


def mk_drive_opt(iostandard, drive):
    if drive is None:
        drive = '_FIXED'
    return '{}.DRIVE.I{}'.format(iostandard, drive)


def skip_broken_tiles(d):
    """ Skip tiles that appear to have bits always set.

    This is likely caused by a defect?

    """
    return False


def drives_for_iostandard(iostandard):
    if iostandard in ['LVTTL', 'LVCMOS18']:
        drives = [2, 4, 6, 8, 12, 16]
    elif iostandard == 'LVCMOS12':
        drives = [2, 4, 6, 8]
    elif iostandard in ('SSTL135', 'SSTL135_DCI', 'SSTL15', 'SSTL15_DCI', 'LVDS'):
        return ['_FIXED']
    else:
        drives = [2, 4, 6, 8, 12, 16]

    return drives


IBUF_LOW_PWR_SUPPORTED = ['SSTL135', 'SSTL15']


def main():
    # Create map of iobank -> sites
    iobanks = {}
    site_to_iobank = {}
    iobank_iostandards = {}
    vccaux = ""
    iobank_inused = set()
    with open(os.path.join(os.getenv('FUZDIR'), 'build', 'iobanks.txt')) as f:
        for l in f:
            iob_site, iobank = l.strip().split(',')
            iobank = int(iobank)

            if iobank not in iobanks:
                iobanks[iobank] = set()

            iobanks[iobank].add(iob_site)
            assert iob_site not in site_to_iobank
            site_to_iobank[iob_site] = iobank

    for iobank in iobanks:
        iobank_iostandards[iobank] = set()

    print("Loading tags")
    segmk = Segmaker("design.bits")
    '''
    port,site,tile,pin,slew,drive,pulltype
    di[0],IOB_X0Y107,LIOB33_X0Y107,A21,PULLDOWN
    di[10],IOB_X0Y147,LIOB33_X0Y147,F14,PULLUP
    '''
    with open('params.json', 'r') as f:
        design = json.load(f)

        diff_pairs = set()
        for d in design['tiles']:
            iostandard = verilog.unquote(d['IOSTANDARD'])
            if iostandard.startswith('DIFF_'):
                diff_pairs.add(d['pair_site'])

        for d in design['tiles']:
            site = d['site']

            if skip_broken_tiles(d):
                continue

            if site in diff_pairs:
                continue

            iostandard = verilog.unquote(d['IOSTANDARD'])
            if iostandard.startswith('DIFF_'):
                iostandard = iostandard[5:]

            iobank_iostandards[site_to_iobank[site]].add(iostandard)

            if 'vccaux' in d:
                vccaux = d['vccaux']

            if 'IN_TERM' in d:
                segmaker.add_site_group_zero(
                    segmk, site, 'IN_TERM.', [
                        'NONE', 'UNTUNED_SPLIT_40', 'UNTUNED_SPLIT_50',
                        'UNTUNED_SPLIT_60'
                    ], 'NONE', d['IN_TERM'])

            if d['type'] is None:
                segmk.add_site_tag(site, '{}.INOUT'.format(iostandard), 0)
                segmk.add_site_tag(site, '{}.IN_USE'.format(iostandard), 0)
                segmk.add_site_tag(site, '{}.IN'.format(iostandard), 0)
                segmk.add_site_tag(site, '{}.OUT'.format(iostandard), 0)
                segmk.add_site_tag(site, '{}.IN_ONLY'.format(iostandard), 0)
            elif d['type'] == 'IBUF':
                segmk.add_site_tag(site, '{}.INOUT'.format(iostandard), 0)
                segmk.add_site_tag(site, '{}.IN_USE'.format(iostandard), 1)
                segmk.add_site_tag(site, '{}.IN'.format(iostandard), 1)
                segmk.add_site_tag(site, '{}.IN_DIFF'.format(iostandard), 0)
                segmk.add_site_tag(site, '{}.OUT'.format(iostandard), 0)
                segmk.add_site_tag(site, '{}.IN_ONLY'.format(iostandard), 1)
                segmk.add_tile_tag(d['tile'], 'IN_DIFF', 0)

                if iostandard in IBUF_LOW_PWR_SUPPORTED:
                    segmk.add_site_tag(site, 'IBUF_LOW_PWR', d['IBUF_LOW_PWR'])
                    segmk.add_site_tag(
                        site, 'ZIBUF_LOW_PWR', 1 ^ d['IBUF_LOW_PWR'])
                iobank_inused.add(site_to_iobank[site])
            elif d['type'] == 'IBUFDS':
                segmk.add_site_tag(site, '{}.INOUT'.format(iostandard), 0)
                if iostandard != 'LVDS':
                    segmk.add_site_tag(site, '{}.IN_USE'.format(iostandard), 1)
                    segmk.add_site_tag(site, '{}.IN_ONLY'.format(iostandard), 1)
                #segmk.add_site_tag(site, '{}.IN'.format(iostandard), 1)
                segmk.add_site_tag(site, '{}.IN_DIFF'.format(iostandard), 1)
                segmk.add_site_tag(site, '{}.OUT'.format(iostandard), 0)
                segmk.add_tile_tag(d['tile'], 'IN_DIFF', 1)
            elif d['type'] == 'OBUF':
                segmk.add_site_tag(site, '{}.INOUT'.format(iostandard), 0)
                segmk.add_site_tag(site, '{}.IN_USE'.format(iostandard), 1)
                segmk.add_site_tag(site, '{}.IN'.format(iostandard), 0)
                segmk.add_site_tag(site, '{}.OUT'.format(iostandard), 1)
                segmk.add_tile_tag(d['tile'], 'OUT_DIFF', 0)
                segmk.add_tile_tag(d['tile'], 'OUT_TRUE_DIFF', 0)
            elif d['type'] == 'OBUFDS':
                segmk.add_site_tag(site, '{}.INOUT'.format(iostandard), 0)
                if iostandard != 'LVDS':
                    segmk.add_site_tag(site, '{}.IN_USE'.format(iostandard), 1)
                    segmk.add_site_tag(site, '{}.IN'.format(iostandard), 0)
                    segmk.add_tile_tag(d['tile'], 'OUT_DIFF', 1)
                    segmk.add_tile_tag(d['tile'], 'OUT_TDIFF', 0)
                    segmk.add_site_tag(site, '{}.OUT'.format(iostandard), 1)
                else:
                    segmk.add_site_tag(site, '{}.IN_DIFF'.format(iostandard), 0)
                    segmk.add_tile_tag(d['tile'], 'OUT_TRUE_DIFF', 1)
                    segmk.add_tile_tag(d['tile'], 'OUT_TRUE_TDIFF', 0)
            elif d['type'] == 'OBUFTDS':
                segmk.add_site_tag(site, '{}.INOUT'.format(iostandard), 0)
                if iostandard != 'LVDS':
                    segmk.add_site_tag(site, '{}.IN_USE'.format(iostandard), 1)
                    segmk.add_site_tag(site, '{}.IN'.format(iostandard), 0)
                    segmk.add_site_tag(site, '{}.OUT'.format(iostandard), 1)
                    segmk.add_tile_tag(d['tile'], 'OUT_DIFF', 1)
                    segmk.add_tile_tag(d['tile'], 'OUT_TDIFF', 1)
                else:
                    segmk.add_site_tag(site, '{}.IN_DIFF'.format(iostandard), 0)
                    segmk.add_tile_tag(d['tile'], 'OUT_TRUE_DIFF', 1)
                    segmk.add_tile_tag(d['tile'], 'OUT_TRUE_TDIFF', 1)
            elif d['type'] == 'IOBUF_DCIEN':
                segmk.add_site_tag(site, '{}.INOUT'.format(iostandard), 1)
                segmk.add_site_tag(site, '{}.IN_USE'.format(iostandard), 1)
                segmk.add_site_tag(site, '{}.IN'.format(iostandard), 1)
                segmk.add_site_tag(site, '{}.OUT'.format(iostandard), 1)
                iobank_inused.add(site_to_iobank[site])
            if d['type'] is not None:
                segmaker.add_site_group_zero(
                    segmk, site, "PULLTYPE.",
                    ("NONE", "KEEPER", "PULLDOWN", "PULLUP"), "PULLDOWN",
                    verilog.unquote(d['PULLTYPE']))

            if d['type'] in [None, 'IBUF', 'IBUFDS'] or iostandard == "LVDS":
                continue

            drive_opts = set()
            for opt in ("LVCMOS18", "LVCMOS15", "LVCMOS12"):
                for drive_opt in ("2", "4", "6", "8", "12", "16"):
                    if drive_opt in ("12", "16") and opt == "LVCMOS12":
                        continue

                    drive_opts.add(mk_drive_opt(opt, drive_opt))

            drive_opts.add(mk_drive_opt("SSTL135", None))
            drive_opts.add(mk_drive_opt("SSTL135_DCI", None))

            drive_opts.add(mk_drive_opt("SSTL15", None))
            drive_opts.add(mk_drive_opt("SSTL15_DCI", None))

            drive_opts.add(mk_drive_opt("LVDS", None))

            segmaker.add_site_group_zero(
                segmk, site, '', drive_opts, mk_drive_opt('LVCMOS18', '12'),
                mk_drive_opt(iostandard, d['DRIVE']))
            if d['SLEW']:
                for opt in ["SLOW", "FAST"]:
                    segmk.add_site_tag(
                        site, iostandard + ".SLEW." + opt, opt == verilog.unquote(
                            d['SLEW']))

            if 'ibufdisable_wire' in d:
                segmk.add_site_tag(
                    site, 'IBUFDISABLE.I', d['ibufdisable_wire'] != '0')

            if 'dcitermdisable_wire' in d:
                segmk.add_site_tag(
                    site, 'DCITERMDISABLE.I', d['dcitermdisable_wire'] != '0')

    site_to_cmt = {}
    site_to_tile = {}
    tile_to_cmt = {}
    cmt_to_idelay = {}
    with open(os.path.join(os.getenv('FUZDIR'), 'build',
                           'cmt_regions.csv')) as f:
        for l in f:
            site, tile, cmt = l.strip().split(',')
            site_to_tile[site] = tile

            site_to_cmt[site] = cmt
            tile_to_cmt[tile] = cmt

            # Given IDELAYCTRL's are only located in HCLK_IOI3 tiles, and
            # there is only on HCLK_IOI3 tile per CMT, update
            # CMT -> IDELAYCTRL / tile map.
            if 'IDELAYCTRL' in site:
                assert cmt not in cmt_to_idelay
                cmt_to_idelay[cmt] = site, tile

    # For each IOBANK with an active VREF set the feature
    cmt_vref_active = set()
    ext_vref_banks = set()
    with open('iobank_vref.csv') as f:
        for l in f:
            iobank, vref = l.strip().split(',')
            if vref == "None":
                ext_vref_banks.add(int(iobank))
                continue
            iobank = int(iobank)

            cmt = None
            for cmt_site in iobanks[iobank]:
                if cmt_site in site_to_cmt:
                    cmt = site_to_cmt[cmt_site]
                    break

            if cmt is None:
                continue

            cmt_vref_active.add(cmt)

            _, hclk_cmt_tile = cmt_to_idelay[cmt]

            opt = 'VREF.V_{:d}_MV'.format(int(float(vref) * 1000))
            segmk.add_tile_tag(hclk_cmt_tile, opt, 1)

    any_dci_used = False

    for iobank in iobank_iostandards:
        if len(iobank_iostandards[iobank]) == 0:
            continue

        for cmt_site in iobanks[iobank]:
            if cmt_site in site_to_cmt:
                cmt = site_to_cmt[cmt_site]
                break

        if cmt is None:
            continue

        _, hclk_cmt_tile = cmt_to_idelay[cmt]

        if "LVDS" in  iobank_iostandards[iobank]:
            iobank_iostandards[iobank].remove("LVDS")

        assert len(iobank_iostandards[iobank]) == 1, iobank_iostandards[iobank]

        iostandard = list(iobank_iostandards[iobank])[0]
        segmk.add_tile_tag(
            hclk_cmt_tile, 'DCI', "_DCI" in iostandard)
        any_dci_used |= "_DCI" in iostandard
        # FIXME:
        vr_tiles = None
        ref_tile = None
        if iobank == 33:
            vr_tiles = ["RIOB18_SING_X43Y0", "RIOB18_SING_X43Y49"]
            ref_tiles = ["RIOB18_X43Y11", "RIOB18_X43Y37"]
        elif iobank == 34:
            vr_tiles = ["RIOB18_SING_X43Y50", "RIOB18_SING_X43Y99"]
            ref_tiles = ["RIOB18_X43Y61", "RIOB18_X43Y87"]
        if vr_tiles is not None:
            segmk.add_tile_tag(
                vr_tiles[0], 'IOB_Y0.VRP_USED', "_DCI" in iostandard)
            segmk.add_tile_tag(
                vr_tiles[1], 'IOB_Y1.VRN_USED', "_DCI" in iostandard)
        if ref_tiles is not None:
            if iostandard in ('SSTL135', 'SSTL135_DCI', 'SSTL15', 'SSTL15_DCI') and iobank in iobank_inused:
                for tile in ref_tiles:
                    segmk.add_tile_tag(tile, 'IOB_Y0.VREF_DRIVER', iobank in ext_vref_banks)
    # For IOBANK's with no active VREF, clear all VREF options.
    for cmt, (_, hclk_cmt_tile) in cmt_to_idelay.items():
        if cmt in cmt_vref_active:
            continue

        for vref in (
                .600,
                .675,
                .75,
                .90,
        ):
            opt = 'VREF.V_{:d}_MV'.format(int(vref * 1000))
            segmk.add_tile_tag(hclk_cmt_tile, opt, 0)

    segmk.compile(bitfilter=bitfilter)
    segmk.write(allow_empty=True)

    # Use a special bitfilter for CFG tiles
    segmk = Segmaker("design.bits")
    cfg_center_mid = "CFG_CENTER_MID_X61Y84"
    segmk.add_tile_tag(
            cfg_center_mid, 'DCI_USED', any_dci_used)
    segmk.compile(bitfilter=lambda f, w: True)
    segmk.write(allow_empty=True)
if __name__ == "__main__":
    main()
