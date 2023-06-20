# -*- encoding: utf-8 -*-
"""
SIGNIFY
signify.app.clienting module

Testing clienting with integration tests that require a running KERIA Cloud Agent
"""
import json
import random
from time import sleep

import requests
from keri.app.keeping import Algos
from keri.core import coring
from responses import _recorder

import pytest
from keri import kering
from keri.core.coring import Tiers, Serder, MtrDex

from signify.app.clienting import SignifyClient
from signify.app.credentialing import Registries

TESTS_APP_DIR = "tests/app/"
WITNESS_FILE_PATH = "{}{}".format(TESTS_APP_DIR,"witness.toml")
DELEGATION_FILE_PATH = "{}{}".format(TESTS_APP_DIR,"delegation.toml")
CONNECT_FILE_PATH = "{}{}".format(TESTS_APP_DIR,"connect.toml")

wit1 = "BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha"
wit2 = "BLskRTInXnMxWaGqcpSyMgo0nYbalW99cGZESrz3zapM"
wit3 = "BIKKuvBwpmDVA4Ds-EpL5bt9OqPzWPja2LigFYZN2YfX"

def test_init():
    url = "http://localhost:3901"
    bran = b'0123456789abcdefghijk'
    tier = None

    # Try with bran that is too short
    with pytest.raises(kering.ConfigurationError):
        SignifyClient(url=url, passcode=bran[:16], tier=tier)

    # Try with an invalid URL
    with pytest.raises(kering.ConfigurationError):
        SignifyClient(url="ftp://www.example.com", passcode=bran, tier=tier)

    client = SignifyClient(url=url, passcode=bran, tier=tier)
    assert client.controller == "ELI7pg979AdhmvrjDeam2eAO2SR5niCgnjAJXJHtJose"
    serder = client.icp
    assert serder.raw == (b'{"v":"KERI10JSON00012b_","t":"icp","d":"ELI7pg979AdhmvrjDeam2eAO2SR5niCgnjAJ'
                          b'XJHtJose","i":"ELI7pg979AdhmvrjDeam2eAO2SR5niCgnjAJXJHtJose","s":"0","kt":"1'
                          b'","k":["DAbWjobbaLqRB94KiAutAHb_qzPpOHm3LURA_ksxetVc"],"nt":"1","n":["EIFG_u'
                          b'qfr1yN560LoHYHfvPAhxQ5sN6xZZT_E3h7d2tL"],"bt":"0","b":[],"c":[],"a":[]}')

    # changing tier with has no effect
    tier = Tiers.low
    client = SignifyClient(url=url, passcode=bran, tier=tier)
    assert client.controller == "ELI7pg979AdhmvrjDeam2eAO2SR5niCgnjAJXJHtJose"

    tier = Tiers.med
    client = SignifyClient(url=url, passcode=bran, tier=tier)
    assert client.controller == "EOgQvKz8ziRn7FdR_ebwK9BkaVOnGeXQOJ87N6hMLrK0"

    tier = Tiers.high
    client = SignifyClient(url=url, passcode=bran, tier=tier)
    assert client.controller == "EB8wN2c_tv1WlsJ5c3949-TFWPMB2IflFbdMlZfC_Hgo"


def test_extern():
    url = "http://localhost:3901"
    bran = b'0123456789abcdefghijk'
    tier = None

    client = SignifyClient(passcode=bran, tier=tier,
                           extern_modules=[
                               dict(
                                   type="gcp",
                                   name="gcp_ksm_shim",
                                   params=dict(
                                       projectId="advance-copilot-319717",
                                       locationId="us-west1",
                                       keyRingId="signify-key-ring"
                                   )
                               )])

    assert client.controller == "ELI7pg979AdhmvrjDeam2eAO2SR5niCgnjAJXJHtJose"
    evt, siger = client.ctrl.event()
    res = requests.post(url="http://localhost:3903/boot",
                        json=dict(
                            icp=evt.ked,
                            sig=siger.qb64,
                            stem=client.ctrl.stem,
                            pidx=1,
                            tier=client.ctrl.tier))

    if res.status_code != requests.codes.accepted:
        raise kering.AuthNError(f"unable to initialize cloud agent connection, {res.status_code}, {res.text}")

    client.connect(url=url)
    assert client.agent is not None
    assert client.agent.delpre == "ELI7pg979AdhmvrjDeam2eAO2SR5niCgnjAJXJHtJose"
    assert client.agent.pre == "EJoqUMpQAfqsJhBqv02ehR-9BJYBTCrW8h5JlLdMTWBg"
    assert client.ctrl.ridx == 0

    # Create AID using external HSM module
    stem = "ABO4qF9g9L-e1QzvMXgY-58elMh8L-63ZBnNXhxScO81"
    identifiers = client.identifiers()
    aid = identifiers.create("aid1", algo=Algos.extern, extern_type="gcp", extern=dict(stem=stem))
    icp = Serder(ked=aid)
    print(icp.pretty())


@_recorder.record(file_path=CONNECT_FILE_PATH)
def test_salty():
    """
    This test assumes a running KERIA agent.
    See integration.sh to run this test automatically with a locally running KERIA and witness network.
    """
    url = "http://localhost:3901"
    bran = b'0123456789abcdefghijk'
    tier = Tiers.med

    client = SignifyClient(passcode=bran, tier=tier)
    assert client.controller == "EOgQvKz8ziRn7FdR_ebwK9BkaVOnGeXQOJ87N6hMLrK0"

    # Raises configuration error because the started agent has a different controller AID
    with pytest.raises(kering.ConfigurationError):
        client.connect(url=url)

    tier = Tiers.low
    client = SignifyClient(passcode=bran, tier=tier)
    assert client.controller == "ELI7pg979AdhmvrjDeam2eAO2SR5niCgnjAJXJHtJose"

    evt, siger = client.ctrl.event()

    print(evt.pretty())
    print(siger.qb64)
    res = requests.post(url="http://localhost:3903/boot",
                        json=dict(
                            icp=evt.ked,
                            sig=siger.qb64,
                            stem=client.ctrl.stem,
                            pidx=1,
                            tier=client.ctrl.tier))

    if res.status_code != requests.codes.accepted:
        raise kering.AuthNError(f"unable to initialize cloud agent connection, {res.status_code}, {res.text}")

    client.connect(url=url)
    assert client.agent is not None
    assert client.agent.pre == "EEXekkGu9IAzav6pZVJhkLnjtjM5v3AcyA-pdKUcaGei"
    assert client.agent.delpre == "ELI7pg979AdhmvrjDeam2eAO2SR5niCgnjAJXJHtJose"

    identifiers = client.identifiers()
    aids = identifiers.list()
    assert aids == []

    op = identifiers.create("aid1", bran="0123456789abcdefghijk")
    aid = op["response"]
    icp = Serder(ked=aid)
    assert icp.pre == "ELUvZ8aJEHAQE-0nsevyYTP98rBbGJUrTj5an-pCmwrK"
    assert len(icp.verfers) == 1
    assert icp.verfers[0].qb64 == "DPmhSfdhCPxr3EqjxzEtF8TVy0YX7ATo0Uc8oo2cnmY9"
    assert len(icp.digers) == 1
    assert icp.digers[0].qb64 == "EAORnRtObOgNiOlMolji-KijC_isa3lRDpHCsol79cOc"
    assert icp.tholder.num == 1
    assert icp.ntholder.num == 1

    rpy = identifiers.makeEndRole(pre=icp.pre, eid="EPGaq6inGxOx-VVVEcUb_KstzJZldHJvVsHqD4IPxTWf")
    print(rpy.pretty())
    assert rpy.ked['a']['cid'] == "ELUvZ8aJEHAQE-0nsevyYTP98rBbGJUrTj5an-pCmwrK"
    assert rpy.ked['a']['eid'] == "EPGaq6inGxOx-VVVEcUb_KstzJZldHJvVsHqD4IPxTWf"

    aids = identifiers.list()
    assert len(aids) == 1
    aid = aids.pop()

    salt = aid[Algos.salty]
    assert aid['name'] == "aid1"
    assert salt["pidx"] == 0
    assert aid["prefix"] == icp.pre
    assert salt["stem"] == "signify:aid"

    op2 = identifiers.create("aid2", count=3, ncount=3, isith="2", nsith="2", bran="0123456789lmnopqrstuv")
    aid2 = op2["response"]
    icp2 = Serder(ked=aid2)
    print(icp2.pre)
    assert icp2.pre == "EP10ooRj0DJF0HWZePEYMLPl-arMV-MAoTKK-o3DXbgX"
    assert len(icp2.verfers) == 3
    assert icp2.verfers[0].qb64 == "DGBw7C7AfC7jbD3jLLRS3SzIWFndM947TyNWKQ52iQx5"
    assert icp2.verfers[1].qb64 == "DD_bHYFsgWXuCbz3SD0HjCIe_ITjRvEoCGuZ4PcNFFDz"
    assert icp2.verfers[2].qb64 == "DEe9u8k0fm1wMFAuOIsCtCNrpduoaV5R21rAcJl0awze"
    assert len(icp2.digers) == 3
    print([diger.qb64 for diger in icp2.digers])
    assert icp2.digers[0].qb64 == "EML5FrjCpz8SEl4dh0U15l8bMRhV_O5iDcR1opLJGBSH"
    assert icp2.digers[1].qb64 == "EJpKquuibYTqpwMDqEFAFs0gwq0PASAHZ_iDmSF3I2Vg"
    assert icp2.digers[2].qb64 == "ELplTAiEKdobFhlf-dh1vUb2iVDW0dYOSzs1dR7fQo60"
    assert icp2.tholder.num == 2
    assert icp2.ntholder.num == 2

    aids = identifiers.list()
    assert len(aids) == 2
    aid = aids[1]
    assert aid['name'] == "aid2"
    assert aid["prefix"] == icp2.pre
    salt = aid[Algos.salty]
    assert salt["pidx"] == 1
    assert salt["stem"] == "signify:aid"

    op3 = identifiers.rotate("aid1")
    ked = op3["response"]
    rot = Serder(ked=ked)

    assert rot.said == "EBQABdRgaxJONrSLcgrdtbASflkvLxJkiDO0H-XmuhGg"
    assert rot.sn == 1
    assert len(rot.digers) == 1
    assert rot.verfers[0].qb64 == "DHgomzINlGJHr-XP3sv2ZcR9QsIEYS3LJhs4KRaZYKly"
    assert rot.digers[0].qb64 == "EJMovBlrBuD6BVeUsGSxLjczbLEbZU9YnTSud9K4nVzk"

    op4 = identifiers.interact("aid1", data=[icp.pre])
    ked = op4["response"]
    ixn = Serder(ked=ked)
    assert ixn.said == "ENsmRAg_oM7Hl1S-GTRMA7s4y760lQMjzl0aqOQ2iTce"
    assert ixn.sn == 2
    assert ixn.ked["a"] == [icp.pre]

    aid = identifiers.get("aid1")
    state = aid["state"]
    assert state['s'] == '2'
    assert state['f'] == '2'
    assert state['et'] == 'ixn'
    assert state['d'] == ixn.said
    assert state['ee']['d'] == rot.said

    events = client.keyEvents()
    log = events.get(pre=aid["prefix"])
    assert len(log) == 3
    serder = coring.Serder(ked=log[0])
    assert serder.pre == icp.pre
    assert serder.said == icp.said
    serder = coring.Serder(ked=log[1])
    assert serder.pre == rot.pre
    assert serder.said == rot.said
    serder = coring.Serder(ked=log[2])
    assert serder.pre == ixn.pre
    assert serder.said == ixn.said

    print(identifiers.list())


@_recorder.record(file_path=WITNESS_FILE_PATH)
def test_witnesses():
    """ This test assumes a running Demo Witnesses and KERIA agent with the following comands:

          `kli witness demo`
          `keria start -c ELI7pg979AdhmvrjDeam2eAO2SR5niCgnjAJXJHtJose \
               --config-file demo-witness-oobis --config-dir <path to KERIpy>/scripts`

    """
    import os
    dir_path = os.path.dirname(os.path.realpath(__file__))
    print("current path: ", dir_path)
    print("should find witenss toml file here: ",os.listdir("{}/../../{}".format(dir_path,TESTS_APP_DIR)))
    url = "http://localhost:3901"
    bran = b'0123456789abcdefghijk'
    tier = Tiers.low

    client = SignifyClient(passcode=bran, tier=tier)
    assert client.controller == "ELI7pg979AdhmvrjDeam2eAO2SR5niCgnjAJXJHtJose"
    evt, siger = client.ctrl.event()
    res = requests.post(url="http://localhost:3903/boot",
                        json=dict(
                            icp=evt.ked,
                            sig=siger.qb64,
                            stem=client.ctrl.stem,
                            pidx=1,
                            tier=client.ctrl.tier))

    if res.status_code != requests.codes.accepted:
        raise kering.AuthNError(f"unable to initialize cloud agent connection, {res.status_code}, {res.text}")

    client.connect(url=url)

    assert client.agent is not None
    assert client.agent.delpre == "ELI7pg979AdhmvrjDeam2eAO2SR5niCgnjAJXJHtJose"
    assert client.agent.pre == 'EEXekkGu9IAzav6pZVJhkLnjtjM5v3AcyA-pdKUcaGei'

    # assert client.ctrl.ridx == 0

    identifiers = client.identifiers()
    operations = client.operations()

    print("creating aid")
    # Use witnesses
    op = identifiers.create("aid1", bran="canIGetAWitnessSaltGreaterThan21", toad="2", wits=["BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha",
                                                    "BLskRTInXnMxWaGqcpSyMgo0nYbalW99cGZESrz3zapM",
                                                    "BIKKuvBwpmDVA4Ds-EpL5bt9OqPzWPja2LigFYZN2YfX"])

    while not op["done"]:
        op = operations.get(op["name"])
        sleep(1)

    icp1 = Serder(ked=op["response"])
    assert icp1.pre == 'EGTFIbnFoA7G-f4FHzzXUMp6VAgQfJ-2nXqzfb5hVwKa'


    assert icp1.ked['b'] == ["BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha",
                             "BLskRTInXnMxWaGqcpSyMgo0nYbalW99cGZESrz3zapM",
                             "BIKKuvBwpmDVA4Ds-EpL5bt9OqPzWPja2LigFYZN2YfX"]
    assert icp1.ked['bt'] == "2"

    aid1 = identifiers.get("aid1")
    assert aid1["prefix"] == icp1.pre
    assert len(aid1["windexes"]) == 3

    aids = identifiers.list()
    assert len(aids) == 1
    aid = aids.pop()
    assert aid['prefix'] == icp1.pre

def test_registry_creation():
    url = "http://localhost:3901"
    booturl = "http://localhost:3903/boot"
    bran = b'0123456789abcdefghijk'
    tier = Tiers.low
    client = SignifyClient(passcode=bran, tier=tier)
    assert client.controller == "ELI7pg979AdhmvrjDeam2eAO2SR5niCgnjAJXJHtJose"
    evt, siger = client.ctrl.event()
    res = requests.post(url=booturl,
                        json=dict(
                            icp=evt.ked,
                            sig=siger.qb64,
                            stem=client.ctrl.stem,
                            pidx=1,
                            tier=client.ctrl.tier))

    client.connect(url=url)

    identifiers = client.identifiers()
    operations = client.operations()

    # TODO use a different AID name and bran
    op = identifiers.create("aid1", bran="canIGetAWitnessSaltGreaterThan21",
                            toad="2", wits=["BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha",
                                            "BLskRTInXnMxWaGqcpSyMgo0nYbalW99cGZESrz3zapM",
                                            "BIKKuvBwpmDVA4Ds-EpL5bt9OqPzWPja2LigFYZN2YfX"])

    while not op["done"]:
        op = operations.get(op["name"])
        sleep(1)

    aid1 = identifiers.get("aid1")

    # Make request to create registry
    registries: Registries = client.registries()
    op = registries.registryIncept(pre=aid1["prefix"],
                                    alias="aid1",
                                    name="myregistry",
                                    body={
                                        "baks": ["BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha",
                                        "BLskRTInXnMxWaGqcpSyMgo0nYbalW99cGZESrz3zapM"],
                                        "toad": 2
                                    })
    while not op["done"]:
        op = operations.get(op["name"])
        sleep(1)

    print(op)


@_recorder.record(file_path=DELEGATION_FILE_PATH)
def test_delegation():
    """ This test assumes a running Demo Witnesses and KERIA agent with the following comands:

          `kli witness demo`
          `keria start \
               --config-file demo-witness-oobis --config-dir <path to KERIpy>/scripts`

    """
    url = "http://localhost:3901"
    bran = b'0123456789abcdefghijk'
    tier = Tiers.low

    client = SignifyClient(passcode=bran, tier=tier)
    print(client.controller)
    assert client.controller == "ELI7pg979AdhmvrjDeam2eAO2SR5niCgnjAJXJHtJose"

    evt, siger = client.ctrl.event()
    res = requests.post(url="http://localhost:3903/boot",
                        json=dict(
                            icp=evt.ked,
                            sig=siger.qb64,
                            stem=client.ctrl.stem,
                            pidx=1,
                            tier=client.ctrl.tier))

    if res.status_code != requests.codes.accepted:
        raise kering.AuthNError(f"unable to initialize cloud agent connection, {res.status_code}, {res.text}")

    client.connect(url=url)
    assert client.agent is not None
    assert client.agent.delpre == "ELI7pg979AdhmvrjDeam2eAO2SR5niCgnjAJXJHtJose"

    # Delegator OOBI:
    # http://127.0.0.1:5642/oobi/EHpD0-CDWOdu5RJ8jHBSUkOqBZ3cXeDVHWNb_Ul89VI7/witness

    delpre = "EHpD0-CDWOdu5RJ8jHBSUkOqBZ3cXeDVHWNb_Ul89VI7"
    identifiers = client.identifiers()
    operations = client.operations()
    oobis = client.oobis()

    op = oobis.resolve(f"http://127.0.0.1:5642/oobi/{delpre}/witness")
    print("OOBI op is: ", op)

    count = 0
    while not op["done"] and not count > 25:
        op = operations.get(op["name"])
        sleep(1)

    op = identifiers.create("aid1", toad="2", delpre=delpre, wits=[wit1, wit2, wit3])
    pre = op["metadata"]["pre"]

    while not op["done"]:
        op = operations.get(op["name"])
        sleep(1)

    icp1 = Serder(ked=op["response"])

    print(icp1.pretty())
    assert icp1.pre == pre


def test_multisig():
    """ This test assumes a running Demo Witnesses and KERIA agent with the following comands:

          `kli witness demo`
          `keria start --config-file demo-witness-oobis --config-dir <path to KERIpy>/scripts`

    """
    url = "http://localhost:3901"
    bran = b'0123456789abcdefghijk'
    tier = Tiers.low

    client = SignifyClient(passcode=bran, tier=tier)
    print(client.controller)
    assert client.controller == "ELI7pg979AdhmvrjDeam2eAO2SR5niCgnjAJXJHtJose"

    evt, siger = client.ctrl.event()
    res = requests.post(url="http://localhost:3903/boot",
                        json=dict(
                            icp=evt.ked,
                            sig=siger.qb64,
                            stem=client.ctrl.stem,
                            pidx=1,
                            tier=client.ctrl.tier))

    client.connect(url=url)
    assert client.agent is not None
    assert client.agent.delpre == "ELI7pg979AdhmvrjDeam2eAO2SR5niCgnjAJXJHtJose"
    assert client.agent.pre == "EEXekkGu9IAzav6pZVJhkLnjtjM5v3AcyA-pdKUcaGei"
    # assert client.ctrl.ridx == 0

    if res.status_code != requests.codes.accepted:
        raise kering.AuthNError(f"unable to initialize cloud agent connection, {res.status_code}, {res.text}")

    identifiers = client.identifiers()
    operations = client.operations()
    oobis = client.oobis()

    op = identifiers.create("multisig3", bran="0123456789lmnopqrstuv")
    icp = op["response"]
    serder = coring.Serder(ked=icp)
    assert serder.pre == "EOGvmhJDBbJP4zeXaRun5vSz0O3_1zB10DwNMyjXlJEv"
    print(f"created AID {serder.pre}")

    identifiers.addEndRole("multisig3", eid=client.agent.pre)

    print(f"OOBI for {serder.pre}:")
    oobi = oobis.get("multisig3")
    print(oobi)

    op = oobis.resolve(oobi="http://127.0.0.1:5642/oobi/EKYLUMmNPZeEs77Zvclf0bSN5IN-mLfLpx2ySb-HDlk4/witness/BBilc4"
                            "-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha",
                       alias="multisig1")

    print("resolving oobi for multisig1")
    while not op["done"]:
        op = operations.get(op["name"])
        sleep(1)

    multisig1 = op["response"]
    print("resolving oobi for multisig2")
    op = oobis.resolve(oobi="http://127.0.0.1:5642/oobi/EJccSRTfXYF6wrUVuenAIHzwcx3hJugeiJsEKmndi5q1/witness/BBilc4"
                            "-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha",
                       alias="multisig2")

    while not op["done"]:
        op = operations.get(op["name"])
        sleep(1)
    multisig2 = op["response"]

    m3 = identifiers.get("multisig3")
    agent0 = m3["state"]
    print(f"agent is {agent0}")

    states = rstates = [multisig2, multisig1, agent0]

    op = identifiers.create("multisig", algo=Algos.group, mhab=m3,
                            isith=["1/3", "1/3", "1/3"], nsith=["1/3", "1/3", "1/3"],
                            toad=3,
                            wits=[
                                "BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha",
                                "BLskRTInXnMxWaGqcpSyMgo0nYbalW99cGZESrz3zapM",
                                "BIKKuvBwpmDVA4Ds-EpL5bt9OqPzWPja2LigFYZN2YfX"
                            ],
                            states=states,
                            rstates=rstates)
    print("waiting on multisig creation...")
    while not op["done"]:
        op = operations.get(op["name"])
        sleep(1)
    gAid = op["response"]
    print(f"group multisig created {gAid}")

    # Join an interaction event with the group
    data = {"i": "EE77q3_zWb5ojgJr-R1vzsL5yiL4Nzm-bfSOQzQl02dy"}
    op = identifiers.interact("multisig", data=data)
    while not op["done"]:
        op = operations.get(op["name"])
        sleep(1)

    ixn = coring.Serder(ked=op["response"])
    events = client.keyEvents()
    log = events.get(pre=ixn.pre)
    assert len(log) == 2

    for event in log:
        print(coring.Serder(ked=event).pretty())

    op2 = identifiers.rotate("multisig3")
    rot = op2["response"]
    serder = coring.Serder(ked=rot)
    print(f"rotated multisig3 to {serder.sn}")

    aid1 = identifiers.get("multisig3")
    agent0 = aid1["state"]
    keyState = client.keyStates()
    op = keyState.query(pre="EKYLUMmNPZeEs77Zvclf0bSN5IN-mLfLpx2ySb-HDlk4", sn=1)
    while not op["done"]:
        op = operations.get(op["name"])
        sleep(1)

    multisig1 = op["response"]
    print(f"using key {multisig1['k'][0]}")
    print(f"using dig {multisig1['n'][0]}")

    op = keyState.query(pre="EJccSRTfXYF6wrUVuenAIHzwcx3hJugeiJsEKmndi5q1", sn=1)
    while not op["done"]:
        op = operations.get(op["name"])
        sleep(1)

    multisig2 = op["response"]
    print(f"using key {multisig2['k'][0]}")
    print(f"using dig {multisig2['n'][0]}")

    states = rstates = [multisig1, multisig2, agent0]

    op = identifiers.rotate("multisig", states=states, rstates=rstates)
    print(op)


def test_randy():
    """ This test assumes a running KERIA agent with the following comand:

          `keria start -c ELI7pg979AdhmvrjDeam2eAO2SR5niCgnjAJXJHtJose`

    """
    url = "http://localhost:3901"
    bran = b'0123456789abcdefghijk'
    tier = Tiers.low
    client = SignifyClient(passcode=bran, tier=tier)
    assert client.controller == "ELI7pg979AdhmvrjDeam2eAO2SR5niCgnjAJXJHtJose"

    evt, siger = client.ctrl.event()
    res = requests.post(url="http://localhost:3903/boot",
                        json=dict(
                            icp=evt.ked,
                            sig=siger.qb64,
                            stem=client.ctrl.stem,
                            pidx=1,
                            tier=client.ctrl.tier))

    if res.status_code != requests.codes.accepted:
        raise kering.AuthNError(f"unable to initialize cloud agent connection, {res.status_code}, {res.text}")

    client.connect(url=url)
    assert client.agent is not None
    assert client.agent.delpre == "ELI7pg979AdhmvrjDeam2eAO2SR5niCgnjAJXJHtJose"
    assert client.agent.pre == "EJoqUMpQAfqsJhBqv02ehR-9BJYBTCrW8h5JlLdMTWBg"
    # assert client.ctrl.ridx == 0

    identifiers = client.identifiers()
    aid = identifiers.create("aid1", algo=Algos.randy)
    icp = Serder(ked=aid)
    assert len(icp.verfers) == 1
    assert len(icp.verfers) == 1
    assert len(icp.digers) == 1
    assert len(icp.digers) == 1
    assert icp.tholder.num == 1
    assert icp.ntholder.num == 1

    aids = identifiers.list()
    assert len(aids) == 1
    aid = aids[0]
    assert aid["prefix"] == icp.pre

    op = identifiers.interact("aid1", data=[icp.pre])
    ked = op["response"]
    ixn = Serder(ked=ked)
    assert ixn.sn == 1
    assert ixn.ked["a"] == [icp.pre]

    aids = identifiers.list()
    assert len(aids) == 1
    aid = aids[0]
    events = client.keyEvents()
    log = events.get(pre=aid["prefix"])
    assert len(log) == 2

    ked = identifiers.rotate("aid1")
    rot = Serder(ked=ked)
    assert rot.pre == icp.pre
    assert rot.sn == 2
    assert len(rot.digers) == 1
    assert rot.verfers[0].qb64 != icp.verfers[0].qb64
    assert rot.digers[0].qb64 != icp.digers[0].qb64
    dig = coring.Diger(ser=rot.verfers[0].qb64b, code=MtrDex.Blake3_256)
    print(icp.digers[0].qb64, dig.qb64)
    assert icp.digers[0].qb64 == dig.qb64
    log = events.get(pre=aid["prefix"])
    assert len(log) == 3

    for event in log:
        print(coring.Serder(ked=event).pretty())


def test_query():
    """ This test assumes a running Demo Witnesses and KERIA agent with the following comands:

          `kli witness demo`
          `keria start -c ELI7pg979AdhmvrjDeam2eAO2SR5niCgnjAJXJHtJose \
               --config-file demo-witness-oobis --config-dir <path to KERIpy>/scripts`

    """
    url = "http://localhost:3901"
    bran = b'0123456789abcdefghijk'
    tier = Tiers.low

    client = SignifyClient(url=url, passcode=bran, tier=tier)
    assert client.controller == "ELI7pg979AdhmvrjDeam2eAO2SR5niCgnjAJXJHtJose"

    client.connect()
    assert client.agent is not None
    assert client.agent.delpre == "ELI7pg979AdhmvrjDeam2eAO2SR5niCgnjAJXJHtJose"
    assert client.agent.pre == "EFebpJik0emPaSuvoSPYuLVpSAsaWVDwf4WYVPOBva_p"
    assert client.ctrl.ridx == 0

    operations = client.operations()
    keyState = client.keyStates()
    op = keyState.query(pre="EKYLUMmNPZeEs77Zvclf0bSN5IN-mLfLpx2ySb-HDlk4")
    while not op["done"]:
        op = operations.get(op["name"])
        sleep(1)

    multisig1 = op["response"]

    op = keyState.query(pre="EJccSRTfXYF6wrUVuenAIHzwcx3hJugeiJsEKmndi5q1")
    while not op["done"]:
        op = operations.get(op["name"])
        sleep(1)

    multisig2 = op["response"]


def test_multi_tenant():
    """ This test assumes a running KERIA agent with the following comand:

          `keria start -c ELI7pg979AdhmvrjDeam2eAO2SR5niCgnjAJXJHtJose`

    """
    url = "http://localhost:3901"
    bran = b'0123456789abcdefghijk'
    tier = Tiers.low
    client = SignifyClient(passcode=bran, tier=tier)
    assert client.controller == "ELI7pg979AdhmvrjDeam2eAO2SR5niCgnjAJXJHtJose"

    evt, siger = client.ctrl.event()
    res = requests.post(url="http://localhost:3903/boot",
                        json=dict(
                            icp=evt.ked,
                            sig=siger.qb64,
                            stem=client.ctrl.stem,
                            pidx=1,
                            tier=client.ctrl.tier))

    if res.status_code != requests.codes.accepted:
        raise kering.AuthNError(f"unable to initialize cloud agent connection, {res.status_code}, {res.text}")

    client.connect(url=url)
    assert client.agent is not None
    assert client.agent.delpre == "ELI7pg979AdhmvrjDeam2eAO2SR5niCgnjAJXJHtJose"
    assert client.agent.pre == "EEXekkGu9IAzav6pZVJhkLnjtjM5v3AcyA-pdKUcaGei"

    identifiers = client.identifiers()
    op = identifiers.create("aid1")
    aid = op["response"]
    icp = Serder(ked=aid)

    # assert icp.pre == "EKGpuLBMAncuGm2mk4F7tEtELqLEl60tT5eGX3sBdCHF"
    print(icp.verfers[0].qb64, icp.digers[0].qb64)
    assert len(icp.verfers) == 1
    # assert icp.verfers[0].qb64 == "DPmhSfdhCPxr3EqjxzEtF8TVy0YX7ATo0Uc8oo2cnmY9"
    assert len(icp.digers) == 1
    # assert icp.digers[0].qb64 == "EAORnRtObOgNiOlMolji-KijC_isa3lRDpHCsol79cOc"
    assert icp.tholder.num == 1
    assert icp.ntholder.num == 1

    identifiers.addEndRole("aid1", eid=client.agent.pre)

    rbran = b'abcdefghijk0123456789'
    rclient = SignifyClient(url=url, passcode=rbran, tier=tier)
    assert rclient.controller == "EIIY2SgE_bqKLl2MlnREUawJ79jTuucvWwh-S6zsSUFo"

    evt, siger = rclient.ctrl.event()
    res = requests.post(url="http://localhost:3903/boot",
                        json=dict(
                            icp=evt.ked,
                            sig=siger.qb64,
                            stem=rclient.ctrl.stem,
                            pidx=1,
                            tier=rclient.ctrl.tier))

    if res.status_code != requests.codes.accepted:
        raise kering.AuthNError(f"unable to initialize cloud agent connection, {res.status_code}, {res.text}")

    rclient.connect()
    assert rclient.agent is not None
    assert rclient.agent.delpre == "EIIY2SgE_bqKLl2MlnREUawJ79jTuucvWwh-S6zsSUFo"
    assert rclient.agent.pre == "ECrQUIn5_aonlPt7zod4HCaqkfG_KPDuUEh8Bql1Y9TY"
    assert rclient.ctrl.ridx == 0

    ridentifiers = rclient.identifiers()
    aid = ridentifiers.create("randy1", algo=Algos.randy)
    icp = Serder(ked=aid)
    assert len(icp.verfers) == 1
    assert len(icp.verfers) == 1
    assert len(icp.digers) == 1
    assert len(icp.digers) == 1
    assert icp.tholder.num == 1
    assert icp.ntholder.num == 1

    ridentifiers.addEndRole("randy1", eid=rclient.agent.pre)
    print(identifiers.list())
    print(ridentifiers.list())


def test_passcode_rotation():
    url = "http://localhost:3901"
    bran = b'0123456789abcdefghijk'
    tier = Tiers.low
    client = SignifyClient(passcode=bran, tier=tier)
    assert client.controller == "ELI7pg979AdhmvrjDeam2eAO2SR5niCgnjAJXJHtJose"

    evt, siger = client.ctrl.event()
    res = requests.post(url="http://localhost:3903/boot",
                        json=dict(
                            icp=evt.ked,
                            sig=siger.qb64,
                            stem=client.ctrl.stem,
                            pidx=1,
                            tier=client.ctrl.tier))

    if res.status_code != requests.codes.accepted:
        raise kering.AuthNError(f"unable to initialize cloud agent connection, {res.status_code}, {res.text}")

    client.connect(url=url)
    assert client.agent is not None
    assert client.agent.delpre == "ELI7pg979AdhmvrjDeam2eAO2SR5niCgnjAJXJHtJose"
    assert client.agent.pre == "EEXekkGu9IAzav6pZVJhkLnjtjM5v3AcyA-pdKUcaGei"

    identifiers = client.identifiers()
    aid = identifiers.create("salty")
    sicp = Serder(ked=aid)

    aid = identifiers.get("salty")
    assert aid["prefix"] == sicp.pre

    aid = identifiers.create("randy", algo=Algos.randy)
    ricp = Serder(ked=aid)

    aid = identifiers.get("randy")
    assert aid["prefix"] == ricp.pre

    identifiers = client.identifiers()
    pres = identifiers.list()
    aids = []
    for pre in pres:
        aid = identifiers.get(name=pre["name"])
        aids.append(aid)

    client.rotate(nbran='0123456789abcdefghijk', aids=aids)
    print(json.dumps(identifiers.list(), indent=1))

    ked = identifiers.rotate("salty")
    rot = Serder(ked=ked)
    print("Salty Rotated:")
    print(rot.pretty())

    ked = identifiers.rotate("randy")
    rot = Serder(ked=ked)
    print("Randy Rotated:")
    print(rot.pretty())


def test_passcode_rotation_x1000():
    url = "http://localhost:3901"
    bran = b'0123456789abcdefghijk'
    tier = Tiers.low
    client = SignifyClient(passcode=bran, tier=tier)
    assert client.controller == "ELI7pg979AdhmvrjDeam2eAO2SR5niCgnjAJXJHtJose"

    evt, siger = client.ctrl.event()
    res = requests.post(url="http://localhost:3903/boot",
                        json=dict(
                            icp=evt.ked,
                            sig=siger.qb64,
                            stem=client.ctrl.stem,
                            pidx=1,
                            tier=client.ctrl.tier))

    if res.status_code != requests.codes.accepted:
        raise kering.AuthNError(f"unable to initialize cloud agent connection, {res.status_code}, {res.text}")

    client.connect(url=url)
    assert client.agent is not None
    assert client.agent.delpre == "ELI7pg979AdhmvrjDeam2eAO2SR5niCgnjAJXJHtJose"
    assert client.agent.pre == "EEXekkGu9IAzav6pZVJhkLnjtjM5v3AcyA-pdKUcaGei"

    identifiers = client.identifiers()

    for idx in range(1000):
        if idx % 10 == 0:
            print(f"Created {idx}...")

        algo = random.choice(["salty", "randy"])
        match algo:
            case "salty":
                aid = identifiers.create(f"salty-{idx}")
                sicp = Serder(ked=aid)

                aid = identifiers.get(f"salty-{idx}")
                assert aid["prefix"] == sicp.pre

            case "randy":
                aid = identifiers.create(f"randy-{idx}", algo=Algos.randy)
                ricp = Serder(ked=aid)

                aid = identifiers.get(f"randy-{idx}")
                assert aid["prefix"] == ricp.pre

    identifiers = client.identifiers()
    pres = identifiers.list()
    print(len(pres))
    # aids = []
    # for pre in pres:
    #     aid = identifiers.get(name=pre["name"])
    #     aids.append(aid)
    #
    # client.rotate(nbran='0123456789abcdefghijk', aids=aids)
    # print(json.dumps(identifiers.list(), indent=1))
    #
    # ked = identifiers.rotate("salty")
    # rot = Serder(ked=ked)
    # print("Salty Rotated:")
    # print(rot.pretty())
    #
    # ked = identifiers.rotate("randy")
    # rot = Serder(ked=ked)
    # print("Randy Rotated:")
    # print(rot.pretty())


def test_recreate_client():
    url = "http://localhost:3901"
    bran = b'0123456789abcdefghijk'
    tier = Tiers.low
    client = SignifyClient(passcode=bran, tier=tier, url=url)
    assert client.controller == "ELI7pg979AdhmvrjDeam2eAO2SR5niCgnjAJXJHtJose"

    identifiers = client.identifiers()
    pres = identifiers.list(limit=1000)

    print(f"loaded {len(pres)} identifiers")
    aids = []
    for pre in pres:
        aid = identifiers.get(name=pre["name"])
        aids.append(aid)

    print("done getting all values, now to rotate")

    client.rotate(nbran='0123456789abcdefghijk', aids=aids)

    print("rotation done, now to list.")
    print(json.dumps(identifiers.list(limit=1000), indent=1))


if __name__ == "__main__":
    # test_delegation()
    # test_witnesses()
    # test_salty()
    # test_randy()
    test_multisig()
    # test_query()
    # test_multi_tenant()
    # test_extern()
    # test_passcode_rotation()
    # test_passcode_rotation_x1000()
    # test_recreate_client()
